"""
Optimized stylesheet manager with parallel processing support.

This module provides an optimized version of StylesheetManager that uses
multiprocessing to apply CSS rules to DOM trees in parallel, significantly
improving performance for large documents.
"""

import os
import re
import logging
import time
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass
import pickle

from html2word.parser.dom_tree import DOMNode
from html2word.parser.css_parser import CSSParser
from html2word.parser.css_selector import CSSSelector
from html2word.parser.performance_monitor import (
    PerformanceMonitor, get_monitor, performance_monitor, Timer
)

logger = logging.getLogger(__name__)


# Configuration - Read at instance initialization time
# Default: parallel enabled with 4 workers (unless overridden by environment variables)
def _get_default_parallel():
    """Get parallel processing setting. Default: True (enabled)."""
    return os.getenv('HTML2WORD_PARALLEL', 'true').lower() == 'true'

def _get_default_monitoring():
    """Get performance monitoring setting. Default: True (enabled)."""
    return os.getenv('HTML2WORD_MONITOR', 'true').lower() == 'true'

def _get_default_workers():
    """Get number of workers. Default: 4 (unless set via HTML2WORD_WORKERS)."""
    return int(os.getenv('HTML2WORD_WORKERS', '4'))


@dataclass
class NodeInfo:
    """Serializable node information for parallel processing."""
    node_id: str  # Unique identifier (path in tree)
    tag: str
    attributes: Dict[str, Any]
    inline_styles: Dict[str, str]
    parent_path: Optional[str] = None
    is_element: bool = True

    @classmethod
    def from_node(cls, node: DOMNode) -> 'NodeInfo':
        """Create NodeInfo from DOMNode."""
        return cls(
            node_id=node.get_path() if hasattr(node, 'get_path') else str(id(node)),
            tag=node.tag,
            attributes=dict(node.attributes) if node.attributes else {},
            inline_styles=dict(node.inline_styles) if node.inline_styles else {},
            parent_path=node.parent.get_path() if node.parent and hasattr(node.parent, 'get_path') else None,
            is_element=node.is_element
        )


class RuleIndex:
    """
    CSS Rule Indexing System for fast candidate rule retrieval.

    This class builds indexes on CSS rules by tag, class, and id to reduce
    the number of rules that need to be checked for each node. Instead of
    checking all 2000+ rules, we only check ~200 candidate rules per node.
    """

    def __init__(self):
        """Initialize empty indexes."""
        self.tag_index: Dict[str, List[Tuple[str, Dict[str, str], Tuple[int, int, int]]]] = {}
        self.class_index: Dict[str, List[Tuple[str, Dict[str, str], Tuple[int, int, int]]]] = {}
        self.id_index: Dict[str, List[Tuple[str, Dict[str, str], Tuple[int, int, int]]]] = {}
        self.wildcard_rules: List[Tuple[str, Dict[str, str], Tuple[int, int, int]]] = []
        self.complex_rules: List[Tuple[str, Dict[str, str], Tuple[int, int, int]]] = []

    def build(self, rules: List[Tuple[str, Dict[str, str], Tuple[int, int, int]]]):
        """
        Build indexes from CSS rules (one-time operation).

        Args:
            rules: List of (selector, styles, specificity) tuples
        """
        # CRITICAL: Store original rules list to preserve CSS cascade order
        self.all_rules = rules

        for rule in rules:
            selector, styles, specificity = rule

            # Analyze selector type and index accordingly
            # IMPORTANT: Use the same rule object (not a new tuple) to preserve identity
            if self._is_wildcard(selector):
                # Wildcard selectors must always be checked
                self.wildcard_rules.append(rule)
            elif self._is_complex(selector):
                # Complex selectors (with combinators) need special handling
                self.complex_rules.append(rule)
                # Also index by rightmost selector for optimization
                self._index_complex_selector(selector, rule)
            else:
                # Simple selectors can be indexed directly
                self._index_simple_selector(selector, rule)

        logger.info(f"Built CSS rule index: {len(self.tag_index)} tags, "
                   f"{len(self.class_index)} classes, {len(self.id_index)} ids, "
                   f"{len(self.wildcard_rules)} wildcards, {len(self.complex_rules)} complex")

    def _is_wildcard(self, selector: str) -> bool:
        """
        Check if selector is a wildcard that must always be checked.

        Args:
            selector: CSS selector string

        Returns:
            True if selector contains wildcard patterns
        """
        # Universal selector
        if selector.strip() == '*':
            return True
        # Attribute selectors (e.g., [type="text"]) - cannot be indexed
        if '[' in selector:
            return True

        # Pseudo-elements (e.g., ::before, ::after) - cannot be indexed
        if '::' in selector:
            return True

        # Some pseudo-classes that are not structure-based should remain as wildcard
        # These are dynamic pseudo-classes that can't be determined from static HTML
        dynamic_pseudos = [':hover', ':active', ':focus', ':visited', ':link', ':target',
                          ':enabled', ':disabled', ':checked', ':indeterminate']
        for pseudo in dynamic_pseudos:
            if pseudo in selector:
                return True

        # Structure-based pseudo-classes like :first-child, :last-child, :nth-child
        # are OK to index because they can be determined from DOM structure
        # So we DON'T mark them as wildcard - let them be indexed normally
        return False

    def _is_complex(self, selector: str) -> bool:
        """
        Check if selector contains combinators (making it complex).

        Args:
            selector: CSS selector string

        Returns:
            True if selector has combinators
        """
        # Check for CSS combinators: descendant, child, adjacent sibling, general sibling
        return any(c in selector for c in [' ', '>', '+', '~', ','])

    def _index_simple_selector(self, selector: str, rule: Tuple[str, Dict[str, str], Tuple[int, int, int]]):
        """
        Index a simple selector (no combinators).

        Extracts tags, classes, and ids from the selector and adds the rule
        to corresponding indexes.

        Args:
            selector: Simple CSS selector (e.g., "div.container#main")
            rule: The complete rule tuple
        """
        # Extract tag name (must be at start)
        tags = re.findall(r'^([a-z][a-z0-9]*)', selector, re.IGNORECASE)

        # Extract class names (.classname)
        classes = re.findall(r'\.([a-zA-Z0-9_-]+)', selector)

        # Extract id (#idname)
        ids = re.findall(r'#([a-zA-Z0-9_-]+)', selector)

        # Add to tag index
        for tag in tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = []
            self.tag_index[tag].append(rule)

        # Add to class index
        for cls in classes:
            if cls not in self.class_index:
                self.class_index[cls] = []
            self.class_index[cls].append(rule)

        # Add to id index
        for id_ in ids:
            if id_ not in self.id_index:
                self.id_index[id_] = []
            self.id_index[id_].append(rule)

    def _index_complex_selector(self, selector: str, rule: Tuple[str, Dict[str, str], Tuple[int, int, int]]):
        """
        Index a complex selector by its rightmost component.

        For complex selectors like "div.container > p.text", we extract the
        rightmost part "p.text" and index it. This is a conservative optimization:
        we may include some false positives, but we won't miss any matches.

        Args:
            selector: Complex CSS selector
            rule: The complete rule tuple
        """
        # Split by combinators and get the rightmost part
        # Handle multiple selectors separated by commas
        parts = selector.split(',')

        for part in parts:
            part = part.strip()
            # Split by combinators (>, +, ~, space)
            components = re.split(r'\s*[>+~]\s*|\s+', part)
            if components:
                rightmost = components[-1].strip()
                if rightmost and not self._is_wildcard(rightmost):
                    # Index the rightmost component
                    self._index_simple_selector(rightmost, rule)

    def get_candidate_rules(self, node_data: Dict[str, Any]) -> List[Tuple[str, Dict[str, str], Tuple[int, int, int]]]:
        """
        Get candidate rules for a node (core optimization).

        This method retrieves only the rules that could potentially match the node,
        dramatically reducing the number of rules to check from ~2000 to ~200.

        IMPORTANT: Maintains CSS cascade order - rules must be returned in the same
        order they appear in the stylesheet for correct specificity handling.

        Args:
            node_data: Dictionary with 'tag', 'attributes', etc.

        Returns:
            List of candidate rules to check (in original order)
        """
        # Collect all potentially matching rules (using set for deduplication by identity)
        candidates_set = set()

        # 1. Index by tag name
        tag = node_data.get('tag', '')
        if tag and tag in self.tag_index:
            for rule in self.tag_index[tag]:
                candidates_set.add(id(rule))  # Use object id for deduplication

        # 2. Index by class names
        attributes = node_data.get('attributes', {})
        node_classes = attributes.get('class', [])

        # Handle both string and list formats
        if isinstance(node_classes, str):
            node_classes = node_classes.split()
        elif not isinstance(node_classes, list):
            node_classes = []

        for cls in node_classes:
            if cls in self.class_index:
                for rule in self.class_index[cls]:
                    candidates_set.add(id(rule))

        # 3. Index by id
        node_id = attributes.get('id')
        if node_id and node_id in self.id_index:
            for rule in self.id_index[node_id]:
                candidates_set.add(id(rule))

        # 4. Always include wildcard rules (conservative: ensures no rule is missed)
        for rule in self.wildcard_rules:
            candidates_set.add(id(rule))

        # 5. Always include complex rules (conservative: ensures no rule is missed)
        for rule in self.complex_rules:
            candidates_set.add(id(rule))

        # CRITICAL: Return rules in their original order from self.all_rules
        # This preserves CSS cascade order for correct style application
        if not hasattr(self, 'all_rules'):
            # Fallback: collect from dict (order not guaranteed, but better than nothing)
            candidates_dict = {}
            for rule_list in [self.tag_index.get(tag, []), *[self.class_index.get(c, []) for c in node_classes],
                            self.id_index.get(node_id, []) if node_id else [],
                            self.wildcard_rules, self.complex_rules]:
                for rule in rule_list:
                    candidates_dict[id(rule)] = rule
            return list(candidates_dict.values())

        # Return candidates in original order
        return [rule for rule in self.all_rules if id(rule) in candidates_set]


class StylesheetManagerOptimized:
    """Optimized stylesheet manager with parallel processing capabilities."""

    def __init__(self):
        """Initialize optimized stylesheet manager."""
        self.rules: List[Tuple[str, Dict[str, str], Tuple[int, int, int]]] = []
        self.css_parser = CSSParser()
        self.css_selector = CSSSelector()

        # CSS Rule Index for fast candidate retrieval
        self.rule_index: Optional[RuleIndex] = None

        # Performance monitoring
        self.monitor = get_monitor() if _get_default_monitoring() else None

        # Parallel processing configuration - Read from environment at initialization time
        self.enable_parallel = _get_default_parallel()
        self.num_workers = _get_default_workers()

        logger.info(f"StylesheetManagerOptimized initialized - Parallel: {self.enable_parallel}, Workers: {self.num_workers}")

    def add_stylesheet(self, css_content: str):
        """
        Add CSS rules from a stylesheet.

        Args:
            css_content: CSS stylesheet content
        """
        parsed_rules = self.css_parser.parse_stylesheet(css_content)

        for selector, styles in parsed_rules:
            specificity = self.css_selector.calculate_specificity(selector)
            self.rules.append((selector, styles, specificity))

        logger.debug(f"Added {len(parsed_rules)} CSS rules from stylesheet")

        if self.monitor:
            self.monitor.metrics.rule_count = len(self.rules)

    def apply_styles_to_node(self, node: DOMNode):
        """
        Apply matching CSS rules to a DOM node (single-threaded version).

        Args:
            node: DOM node to apply styles to
        """
        if not node.is_element:
            return

        node_timer = Timer("apply_node") if self.monitor else None
        if node_timer:
            node_timer.start()

        # Collect matching rules with their specificity
        matching_rules: List[Tuple[Dict[str, str], Tuple[int, int, int]]] = []

        for selector, styles, specificity in self.rules:
            if self.monitor:
                with self.monitor.timer('selector_match'):
                    matches = self.css_selector.matches(selector, node)
            else:
                matches = self.css_selector.matches(selector, node)

            if matches:
                matching_rules.append((styles, specificity))
                if self.monitor:
                    self.monitor.metrics.match_count += 1

        if matching_rules:
            # Sort by specificity (low to high)
            matching_rules.sort(key=lambda x: x[1])

            # Apply styles in order of specificity
            css_styles = {}

            for styles, specificity in matching_rules:
                # DEBUG: Track border-left property updates
                has_border_left = any(k.startswith('border-left') for k in styles.keys())
                if has_border_left:
                    logger.debug(f"Sequential: Rule with specificity {specificity} adds border-left properties: {[k for k in styles.keys() if k.startswith('border-left')]}")

                css_styles.update(styles)

            # DEBUG: Log final border-left values before merge
            border_left_props = {k: v for k, v in css_styles.items() if k.startswith('border-left')}
            if border_left_props:
                logger.debug(f"Sequential: Final border-left styles for {node.tag}: {border_left_props}")

            # Merge CSS styles into node's inline styles
            if self.monitor:
                with self.monitor.timer('style_merge'):
                    for prop, value in css_styles.items():
                        if prop not in node.inline_styles:
                            node.inline_styles[prop] = value
            else:
                for prop, value in css_styles.items():
                    if prop not in node.inline_styles:
                        node.inline_styles[prop] = value

            logger.debug(f"Applied {len(matching_rules)} CSS rules to {node.tag}")

        if node_timer:
            elapsed = node_timer.stop()
            self.monitor.record_node_time(elapsed)

    def apply_styles_to_tree(self, node: DOMNode, use_optimization: Optional[bool] = None):
        """
        Apply CSS rules to entire DOM tree with optional parallel processing.

        Args:
            node: Root node of tree
            use_optimization: Override parallel processing setting
        """
        use_parallel = self.enable_parallel if use_optimization is None else use_optimization

        if use_parallel and self.num_workers > 1:
            return self.apply_styles_to_tree_parallel(node)
        else:
            return self.apply_styles_to_tree_sequential(node)

    @performance_monitor
    def apply_styles_to_tree_sequential(self, node: DOMNode):
        """
        Apply CSS rules to DOM tree sequentially (original implementation).

        Args:
            node: Root node of tree
        """
        logger.info("Applying CSS rules to DOM tree (sequential mode)...")
        start_time = time.perf_counter()

        node_count = [0]

        def traverse(current_node: DOMNode):
            node_count[0] += 1
            if node_count[0] % 500 == 0:
                logger.info(f"Applied styles to {node_count[0]} DOM nodes...")

            self.apply_styles_to_node(current_node)

            for child in current_node.children:
                traverse(child)

        traverse(node)

        elapsed = time.perf_counter() - start_time
        logger.info(f"Completed applying styles to {node_count[0]} DOM nodes in {elapsed:.2f}s")

        if self.monitor:
            self.monitor.metrics.node_count = node_count[0]
            self.monitor.metrics.total_time = elapsed

    @performance_monitor
    def apply_styles_to_tree_parallel(self, node: DOMNode):
        """
        Apply CSS rules to DOM tree using parallel processing.

        Args:
            node: Root node of tree
        """
        logger.info(f"Applying CSS rules to DOM tree (parallel mode with {self.num_workers} workers)...")
        start_time = time.perf_counter()

        # Step 0: Build rule index if not already built (one-time operation)
        if self.rule_index is None:
            logger.info("Building CSS rule index...")
            index_start = time.perf_counter()
            self.rule_index = RuleIndex()
            self.rule_index.build(self.rules)
            index_time = time.perf_counter() - index_start
            logger.info(f"CSS rule index built in {index_time:.3f}s")

        # Step 1: Collect all nodes with their paths
        all_nodes_with_paths = self._collect_all_nodes_with_paths(node)
        logger.info(f"Collected {len(all_nodes_with_paths)} nodes for parallel processing")

        if len(all_nodes_with_paths) == 0:
            return

        # Step 2: Split into chunks
        chunks = self._split_node_paths_into_chunks(all_nodes_with_paths, self.num_workers)
        logger.info(f"Split nodes into {len(chunks)} chunks")

        # Step 3: Prepare full DOM tree for parallel processing
        dom_tree_full = self._serialize_full_dom_tree(node)

        # Step 4: Process chunks in parallel
        results = []
        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            # Submit all tasks
            futures = []
            for i, chunk in enumerate(chunks):
                # Prepare chunk data: list of (path, node_data) tuples
                chunk_data = []
                for node_path, node_obj in chunk:
                    node_data = {
                        'tag': node_obj.tag,
                        'attributes': dict(node_obj.attributes) if node_obj.attributes else {},
                        'inline_styles': dict(node_obj.inline_styles) if node_obj.inline_styles else {},
                    }
                    chunk_data.append((node_path, node_data))

                # Pass rule_index instead of rules for indexed lookup
                future = executor.submit(
                    process_chunk_worker_indexed,
                    chunk_data,
                    self.rule_index,
                    dom_tree_full,
                    i
                )
                futures.append(future)

            # Collect results
            for future in as_completed(futures):
                try:
                    chunk_results = future.result(timeout=300)  # 5 minute timeout
                    results.extend(chunk_results)
                    logger.debug(f"Processed chunk with {len(chunk_results)} results")
                except Exception as e:
                    logger.error(f"Error processing chunk: {e}")
                    # Fallback to sequential processing
                    logger.warning("Falling back to sequential processing due to parallel error")
                    return self.apply_styles_to_tree_sequential(node)

        # Step 5: Merge results back to nodes
        self._merge_results_by_path(results, all_nodes_with_paths)

        elapsed = time.perf_counter() - start_time
        logger.info(f"Completed parallel processing of {len(all_nodes_with_paths)} nodes in {elapsed:.2f}s")
        logger.info(f"Speedup: {self.num_workers:.1f}x theoretical, actual speedup will vary")

        if self.monitor:
            self.monitor.metrics.node_count = len(all_nodes_with_paths)
            self.monitor.metrics.total_time = elapsed
            self.monitor.finalize()

    def _collect_all_nodes(self, root: DOMNode) -> List[DOMNode]:
        """
        Collect all element nodes from DOM tree using depth-first traversal.

        Args:
            root: Root node of tree

        Returns:
            List of all element nodes
        """
        nodes = []

        def traverse(node: DOMNode):
            if node.is_element:
                nodes.append(node)
            for child in node.children:
                traverse(child)

        traverse(root)
        return nodes

    def _collect_all_nodes_with_paths(self, root: DOMNode) -> List[Tuple[str, DOMNode]]:
        """
        Collect all element nodes with their paths from DOM tree.

        Args:
            root: Root node of tree

        Returns:
            List of (path, node) tuples
        """
        nodes_with_paths = []

        # Use the actual root tag instead of hardcoding "/root"
        root_path = f"/{root.tag}" if root.tag else "/root"

        def traverse(node: DOMNode, path: str):
            if node.is_element:
                nodes_with_paths.append((path, node))

            # Track child index among element children only
            element_index = 0
            for child in node.children:
                if child.is_element:
                    child_path = f"{path}/{child.tag}[{element_index}]"
                    traverse(child, child_path)
                    element_index += 1

        traverse(root, root_path)
        return nodes_with_paths

    def _split_into_chunks(self, nodes: List[DOMNode], num_chunks: int) -> List[List[DOMNode]]:
        """
        Split node list into approximately equal chunks for parallel processing.

        Args:
            nodes: List of nodes to split
            num_chunks: Number of chunks to create

        Returns:
            List of node chunks
        """
        if num_chunks <= 1:
            return [nodes]

        chunk_size = max(1, len(nodes) // num_chunks)
        chunks = []

        for i in range(0, len(nodes), chunk_size):
            chunk = nodes[i:i + chunk_size]
            if chunk:
                chunks.append(chunk)

        # Merge last chunk if it's too small
        if len(chunks) > num_chunks and len(chunks[-1]) < chunk_size // 2:
            chunks[-2].extend(chunks[-1])
            chunks.pop()

        return chunks

    def _split_node_paths_into_chunks(self, nodes_with_paths: List[Tuple[str, DOMNode]], num_chunks: int) -> List[List[Tuple[str, DOMNode]]]:
        """
        Split node list with paths into approximately equal chunks for parallel processing.

        Args:
            nodes_with_paths: List of (path, node) tuples to split
            num_chunks: Number of chunks to create

        Returns:
            List of chunks containing (path, node) tuples
        """
        if num_chunks <= 1:
            return [nodes_with_paths]

        chunk_size = max(1, len(nodes_with_paths) // num_chunks)
        chunks = []

        for i in range(0, len(nodes_with_paths), chunk_size):
            chunk = nodes_with_paths[i:i + chunk_size]
            if chunk:
                chunks.append(chunk)

        # Merge last chunk if it's too small
        if len(chunks) > num_chunks and len(chunks[-1]) < chunk_size // 2:
            chunks[-2].extend(chunks[-1])
            chunks.pop()

        return chunks

    def _serialize_dom_tree(self, root: DOMNode) -> Dict[str, Any]:
        """
        Serialize DOM tree for passing to worker processes.

        Args:
            root: Root node of tree

        Returns:
            Serialized tree data
        """
        # For now, we'll create a simple mapping of paths to nodes
        # This allows descendant selectors to work
        tree_map = {}

        def traverse(node: DOMNode, path: str = ""):
            node_path = f"{path}/{node.tag}[{node.position}]" if hasattr(node, 'position') else f"{path}/{node.tag}"

            tree_map[node_path] = {
                'tag': node.tag,
                'attributes': dict(node.attributes) if node.attributes else {},
                'parent_path': path if path else None,
                'children_paths': []
            }

            for i, child in enumerate(node.children):
                if child.is_element:
                    child_path = traverse(child, node_path)
                    tree_map[node_path]['children_paths'].append(child_path)

            return node_path

        traverse(root)
        return tree_map

    def _serialize_full_dom_tree(self, root: DOMNode) -> Dict[str, Tuple[Dict[str, Any], List[str]]]:
        """
        Serialize complete DOM tree for parallel processing.

        Args:
            root: Root node of tree

        Returns:
            Dict mapping paths to (node_data, children_paths) tuples
        """
        tree_map = {}

        # Use the actual root tag to match _collect_all_nodes_with_paths
        root_path = f"/{root.tag}" if root.tag else "/root"

        def traverse(node: DOMNode, path: str):
            # Store node data
            node_data = {
                'tag': node.tag,
                'attributes': dict(node.attributes) if node.attributes else {},
                'inline_styles': dict(node.inline_styles) if node.inline_styles else {},
            }

            children_paths = []
            element_index = 0
            for child in node.children:
                if child.is_element:
                    child_path = f"{path}/{child.tag}[{element_index}]"
                    children_paths.append(child_path)
                    traverse(child, child_path)
                    element_index += 1

            tree_map[path] = (node_data, children_paths)

        traverse(root, root_path)
        return tree_map

    def _merge_results(self, results: List[Tuple[str, Dict[str, str]]], nodes: List[DOMNode]):
        """
        Merge computed styles from worker processes back to DOM nodes.

        Args:
            results: List of (node_id, css_styles) tuples
            nodes: Original node list
        """
        # Create mapping for fast lookup
        node_map = {}
        for node in nodes:
            node_id = node.get_path() if hasattr(node, 'get_path') else str(id(node))
            node_map[node_id] = node

        # Apply results
        for node_id, css_styles in results:
            if node_id in node_map:
                node = node_map[node_id]

                # Merge styles (inline styles have priority)
                for prop, value in css_styles.items():
                    if prop not in node.inline_styles:
                        node.inline_styles[prop] = value

                logger.debug(f"Merged {len(css_styles)} styles to node {node.tag}")

    def _merge_results_by_path(self, results: List[Tuple[str, Dict[str, str]]], nodes_with_paths: List[Tuple[str, DOMNode]]):
        """
        Merge computed styles from worker processes back to DOM nodes using paths.

        Args:
            results: List of (node_path, css_styles) tuples from workers
            nodes_with_paths: Original list of (path, node) tuples
        """
        # Create mapping for fast lookup
        path_to_node = {path: node for path, node in nodes_with_paths}

        # Apply results
        merged_count = 0
        for node_path, css_styles in results:
            if node_path in path_to_node:
                node = path_to_node[node_path]

                # Merge styles (inline styles have priority)
                for prop, value in css_styles.items():
                    if prop not in node.inline_styles:
                        node.inline_styles[prop] = value

                if css_styles:
                    merged_count += 1
                    logger.debug(f"Merged {len(css_styles)} styles to {node.tag} at {node_path}")

        logger.info(f"Merged styles to {merged_count} nodes out of {len(results)} processed")

    def clear(self):
        """Clear all CSS rules."""
        self.rules.clear()

    def get_rule_count(self) -> int:
        """Get the number of CSS rules."""
        return len(self.rules)

    def get_performance_metrics(self) -> Optional[Dict[str, Any]]:
        """Get performance metrics if monitoring is enabled."""
        if self.monitor:
            return self.monitor.get_metrics().to_dict()
        return None


# Worker function for parallel processing (must be at module level for pickling)
def process_chunk_worker(
    chunk_nodes: List[Tuple[str, Dict[str, Any]]],
    rules: List[Tuple[str, Dict[str, str], Tuple[int, int, int]]],
    dom_tree_full: Dict[str, Tuple[Dict[str, Any], List[str]]],
    chunk_id: int
) -> List[Tuple[str, Dict[str, str]]]:
    """
    Process a chunk of nodes in a worker process.

    Args:
        chunk_nodes: List of (node_path, node_data) tuples to process
        rules: CSS rules to apply
        dom_tree_full: Full DOM tree as (node_data, children_paths) dict
        chunk_id: Chunk identifier for logging

    Returns:
        List of (node_path, computed_styles) tuples
    """
    # Import inside worker to avoid serialization issues
    from html2word.parser.css_selector import CSSSelector

    # Create a local CSS selector for this process
    css_selector = CSSSelector()
    results = []

    # Build a lightweight node wrapper for CSS matching
    class LightweightNode:
        def __init__(self, path: str, data: Dict[str, Any], tree: Dict):
            self.path = path
            self.tag = data['tag']
            self.attributes = data.get('attributes', {})
            self.inline_styles = data.get('inline_styles', {})
            self.is_element = True
            self._tree = tree
            self._parent = None
            self._children = None

        @property
        def parent(self):
            if self._parent is None:
                # Handle root node - check if path has only one slash
                if self.path.count('/') == 1:  # e.g., "/[document]" or "/html"
                    return None

                # Extract parent path
                parts = self.path.rsplit('/', 1)
                if len(parts) > 1 and parts[0]:
                    parent_path = parts[0]
                    if parent_path in self._tree:
                        parent_data, _ = self._tree[parent_path]
                        self._parent = LightweightNode(parent_path, parent_data, self._tree)
            return self._parent

        @property
        def children(self):
            if self._children is None:
                self._children = []
                if self.path in self._tree:
                    _, child_paths = self._tree[self.path]
                    for child_path in child_paths:
                        if child_path in self._tree:
                            child_data, _ = self._tree[child_path]
                            self._children.append(LightweightNode(child_path, child_data, self._tree))
            return self._children

    # Process each node in the chunk
    for node_path, node_data in chunk_nodes:
        # Create lightweight node for CSS matching
        node = LightweightNode(node_path, node_data, dom_tree_full)

        # Collect matching rules with their specificity
        matching_rules = []

        for selector, styles, specificity in rules:
            try:
                if css_selector.matches(selector, node):
                    matching_rules.append((styles, specificity))
            except Exception as e:
                # Log but don't fail on individual selector errors
                import traceback
                logger.debug(f"Worker {chunk_id}: Error matching selector '{selector}': {e}")
                if chunk_id == 0 and node_path == chunk_nodes[0][0]:  # Log first error in detail
                    logger.debug(f"Full traceback: {traceback.format_exc()}")
                continue

        if matching_rules:
            # Sort by specificity (low to high)
            matching_rules.sort(key=lambda x: x[1])

            # Apply styles in order of specificity
            css_styles = {}
            for styles, _ in matching_rules:
                css_styles.update(styles)

            # Only include styles not in inline_styles
            filtered_styles = {
                prop: value
                for prop, value in css_styles.items()
                if prop not in node.inline_styles
            }

            results.append((node_path, filtered_styles))
        else:
            # Even if no matching rules, include empty styles for completeness
            results.append((node_path, {}))

    return results


def process_chunk_worker_indexed(
    chunk_nodes: List[Tuple[str, Dict[str, Any]]],
    rule_index: RuleIndex,
    dom_tree_full: Dict[str, Tuple[Dict[str, Any], List[str]]],
    chunk_id: int
) -> List[Tuple[str, Dict[str, str]]]:
    """
    Process a chunk of nodes in a worker process using indexed rule lookup.

    This is the optimized version that uses RuleIndex to reduce the number
    of rules checked per node from ~2000 to ~200, providing 5-10x speedup.

    Args:
        chunk_nodes: List of (node_path, node_data) tuples to process
        rule_index: Pre-built RuleIndex for fast candidate retrieval
        dom_tree_full: Full DOM tree as (node_data, children_paths) dict
        chunk_id: Chunk identifier for logging

    Returns:
        List of (node_path, computed_styles) tuples
    """
    # Import inside worker to avoid serialization issues
    from html2word.parser.css_selector import CSSSelector
    import logging

    logger = logging.getLogger(__name__)

    # Create a local CSS selector for this process
    css_selector = CSSSelector()
    results = []

    # Build a lightweight node wrapper for CSS matching
    class LightweightNode:
        def __init__(self, path: str, data: Dict[str, Any], tree: Dict):
            self.path = path
            self.tag = data['tag']
            self.attributes = data.get('attributes', {})
            self.inline_styles = data.get('inline_styles', {})
            self.is_element = True
            self._tree = tree
            self._parent = None
            self._children = None

        @property
        def parent(self):
            if self._parent is None:
                # Handle root node - check if path has only one slash
                if self.path.count('/') == 1:  # e.g., "/[document]" or "/html"
                    return None

                # Extract parent path
                parts = self.path.rsplit('/', 1)
                if len(parts) > 1 and parts[0]:
                    parent_path = parts[0]
                    if parent_path in self._tree:
                        parent_data, _ = self._tree[parent_path]
                        self._parent = LightweightNode(parent_path, parent_data, self._tree)
            return self._parent

        @property
        def children(self):
            if self._children is None:
                self._children = []
                if self.path in self._tree:
                    _, child_paths = self._tree[self.path]
                    for child_path in child_paths:
                        if child_path in self._tree:
                            child_data, _ = self._tree[child_path]
                            self._children.append(LightweightNode(child_path, child_data, self._tree))
            return self._children

    # Process each node in the chunk
    total_candidates = 0
    total_matches = 0

    for node_path, node_data in chunk_nodes:
        # 🔑 KEY OPTIMIZATION: Use index to get candidate rules (from ~2000 to ~200)
        candidate_rules = rule_index.get_candidate_rules(node_data)
        total_candidates += len(candidate_rules)

        # Create lightweight node for CSS matching (only if we have candidates)
        if candidate_rules:
            node = LightweightNode(node_path, node_data, dom_tree_full)

            # Collect matching rules with their specificity
            matching_rules = []

            for selector, styles, specificity in candidate_rules:
                try:
                    if css_selector.matches(selector, node):
                        matching_rules.append((styles, specificity))
                        total_matches += 1
                except Exception as e:
                    # Log but don't fail on individual selector errors
                    logger.debug(f"Worker {chunk_id}: Error matching selector '{selector}': {e}")
                    continue

            if matching_rules:
                # Sort by specificity (low to high)
                matching_rules.sort(key=lambda x: x[1])

                # Apply styles in order of specificity
                css_styles = {}
                for styles, specificity in matching_rules:
                    # DEBUG: Track border-left property updates
                    has_border_left = any(k.startswith('border-left') for k in styles.keys())
                    if has_border_left:
                        logger.debug(f"Worker {chunk_id}: Rule with specificity {specificity} adds border-left properties: {[k for k in styles.keys() if k.startswith('border-left')]}")

                    css_styles.update(styles)

                # Only include styles not in inline_styles
                filtered_styles = {
                    prop: value
                    for prop, value in css_styles.items()
                    if prop not in node.inline_styles
                }

                # DEBUG: Log final border-left values for this node
                border_left_props = {k: v for k, v in filtered_styles.items() if k.startswith('border-left')}
                if border_left_props:
                    logger.debug(f"Worker {chunk_id}: Final border-left styles for {node_data.get('tag', 'unknown')}: {border_left_props}")

                results.append((node_path, filtered_styles))
            else:
                # Even if no matching rules, include empty styles for completeness
                results.append((node_path, {}))
        else:
            # No candidates, no styles to apply
            results.append((node_path, {}))

    # Log indexing effectiveness
    avg_candidates = total_candidates / len(chunk_nodes) if chunk_nodes else 0
    logger.debug(f"Worker {chunk_id}: Processed {len(chunk_nodes)} nodes, "
                f"avg {avg_candidates:.1f} candidates/node, {total_matches} matches")

    return results


# Backward compatibility
class StylesheetManager(StylesheetManagerOptimized):
    """Alias for backward compatibility."""
    pass