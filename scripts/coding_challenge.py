#!/usr/bin/env python3
"""
Coding Challenge System — Sig Botti's Practice Framework
Directly addresses coding gap (2/5 benchmark).

Usage:
  python3 scripts/coding_challenge.py              # Run all challenges
  python3 scripts/coding_challenge.py --list        # List challenges
  python3 scripts/coding_challenge.py --history     # Show history
  python3 scripts/coding_challenge.py --challenge 3 # Run specific challenge
  python3 scripts/coding_challenge.py --practice    # 5 random easy/medium
"""

import sys
import json
import time
import random
import statistics
import hashlib
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE = Path("/Users/sigbotti/.openclaw/workspace")
HISTORY_FILE = WORKSPACE / "memory" / "coding_challenge_history.json"
LOG_FILE = WORKSPACE / "memory" / "execution-log.md"

# ─────────────────────────────────────────────────────────────
# CHALLENGES — each returns (output, passed_tests, total_tests)
# ─────────────────────────────────────────────────────────────

def challenge_1_fizzbuzz():
    """Easy — FizzBuzz. Classic warmup."""
    output = []
    for i in range(1, 21):
        if i % 15 == 0:
            output.append("FizzBuzz")
        elif i % 3 == 0:
            output.append("Fizz")
        elif i % 5 == 0:
            output.append("Buzz")
        else:
            output.append(str(i))
    
    # Validate: 15th = FizzBuzz, 10th = Buzz, 3rd = Fizz
    checks = [
        output[0] == "1",
        output[2] == "Fizz",
        output[4] == "Buzz",
        output[9] == "Buzz",
        output[14] == "FizzBuzz",
        len(output) == 20,
    ]
    return "\n".join(output), sum(checks), len(checks)


def challenge_2_palindrome():
    """Easy — Check if a number is a palindrome without converting to string."""
    def is_palindrome(n):
        if n < 0:
            return False
        original = n
        rev = 0
        while n > 0:
            rev = rev * 10 + n % 10
            n //= 10
        return original == rev

    tests = [(121, True), (123, False), (0, True), (1001, True), (-121, False), (11, True)]
    results = [is_palindrome(a) == b for a, b in tests]
    failed = [(a, b, is_palindrome(a)) for a, b in tests if is_palindrome(a) != b]
    output = f"Palindrome tests: {sum(results)}/{len(results)} passed"
    if failed:
        output += f"\nFailed: {failed}"
    return output, sum(results), len(results)


def challenge_3_linked_list():
    """Medium — Implement a singly linked list with append and has_cycle."""
    class Node:
        def __init__(self, val=0, next=None):
            self.val = val
            self.next = next
    
    class LinkedList:
        def __init__(self):
            self.head = None
        
        def append(self, val):
            if not self.head:
                self.head = Node(val)
                return
            curr = self.head
            while curr.next:
                curr = curr.next
            curr.next = Node(val)
        
        def has_cycle(self):
            slow = self.head
            fast = self.head
            while fast and fast.next:
                slow = slow.next
                fast = fast.next.next
                if slow == fast:
                    return True
            return False
    
    ll = LinkedList()
    for v in [1, 2, 3, 4]:
        ll.append(v)
    
    checks = [
        ll.has_cycle() == False,
        ll.head.val == 1,
        ll.head.next.next.val == 3,
    ]
    
    # Add a cycle and re-test
    ll.head.next.next.next.next = ll.head  # cycle
    checks.append(ll.has_cycle() == True)
    
    return "LinkedList: append + cycle detection working", sum(checks), len(checks)


def challenge_4_binary_search():
    """Easy — Binary search on sorted array."""
    def bsearch(arr, target):
        lo, hi = 0, len(arr) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                lo = mid + 1
            else:
                hi = mid - 1
        return -1
    
    arr = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25]
    tests = [(7, 3), (1, 0), (25, 12), (99, -1), (15, 7)]
    results = [bsearch(arr, t) == i for t, i in tests]
    return f"Binary search: {sum(results)}/{len(results)} passed", sum(results), len(results)


def challenge_5_topological_sort():
    """Medium — Topological sort using Kahn's algorithm."""
    from collections import deque, defaultdict
    
    def topo_sort(n, edges):
        g = defaultdict(list)
        indeg = [0] * n
        for u, v in edges:
            g[u].append(v)
            indeg[v] += 1
        
        q = deque([i for i in range(n) if indeg[i] == 0])
        result = []
        while q:
            node = q.popleft()
            result.append(node)
            for nb in g[node]:
                indeg[nb] -= 1
                if indeg[nb] == 0:
                    q.append(nb)
        return result if len(result) == n else []
    
    # Test 1: DAG with 4 nodes and clear ordering
    # 0 → 1 → 2 → 3 (simple chain)
    edges1 = [(0, 1), (1, 2), (2, 3)]
    result1 = topo_sort(4, edges1)
    checks1 = [
        len(result1) == 4,
        result1.index(0) < result1.index(1) < result1.index(2) < result1.index(3),
    ]
    
    # Test 2: 0 is source, 3 is sink, 1 and 2 independent
    # edges = [(1,0), (2,0), (3,1), (3,2)] → 0 must come before 1,2, and 1,2 before 3
    edges2 = [(1, 0), (2, 0), (3, 1), (3, 2)]
    result2 = topo_sort(4, edges2)
    valid2 = (result2.index(0) < result2.index(1) and 
              result2.index(0) < result2.index(2) and 
              result2.index(1) < result2.index(3) and 
              result2.index(2) < result2.index(3))
    checks2 = [len(result2) == 4, valid2]
    
    # Test 3: cycle detection — should return empty
    edges3 = [(0, 1), (1, 2), (2, 0)]
    result3 = topo_sort(3, edges3)
    checks3 = [result3 == []]
    
    passed = sum(checks1) + sum(checks2) + sum(checks3)
    total = len(checks1) + len(checks2) + len(checks3)
    return f"Topo sort: {passed}/{total} passed", passed, total


def challenge_6_lru_cache():
    """Medium — LRU Cache with O(1) get and put."""
    from collections import OrderedDict
    
    class LRUCache:
        def __init__(self, capacity):
            self.cap = capacity
            self.cache = OrderedDict()
        
        def get(self, key):
            if key not in self.cache:
                return -1
            self.cache.move_to_end(key)
            return self.cache[key]
        
        def put(self, key, val):
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = val
            if len(self.cache) > self.cap:
                self.cache.popitem(last=False)
    
    cache = LRUCache(2)
    ops = [("put", 1, 1), ("put", 2, 2), ("get", 1, None), ("put", 3, 3),
           ("get", 2, None), ("put", 4, 4), ("get", 1, None), ("get", 3, None), ("get", 4, None)]
    expected = [None, None, 1, None, -1, None, -1, 3, 4]
    
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    r1 = cache.get(1)
    cache.put(3, 3)
    r2 = cache.get(2)
    cache.put(4, 4)
    r3 = cache.get(1)
    r4 = cache.get(3)
    r5 = cache.get(4)
    
    checks = [
        r1 == 1,   # get 1 → 1
        r2 == -1,  # get 2 → -1 (evicted)
        r3 == -1,  # get 1 → -1 (evicted)
        r4 == 3,   # get 3
        r5 == 4,   # get 4
    ]
    return f"LRU cache: {sum(checks)}/{len(checks)} passed", sum(checks), len(checks)


def challenge_7_string_algo():
    """Medium — Longest common subsequence (LCS)."""
    def lcs(a, b):
        n, m = len(a), len(b)
        dp = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for j in range(1, m + 1):
                if a[i-1] == b[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        return dp[n][m]
    
    tests = [
        ("abcde", "ace", 3),     # LCS = "ace"
        ("abc", "abc", 3),        # identical
        ("abc", "def", 0),        # no common
        ("AGGTAB", "GXTXAYB", 4), # LCS = "GTAB"
    ]
    results = [lcs(a, b) == exp for a, b, exp in tests]
    return f"LCS: {sum(results)}/{len(results)} passed", sum(results), len(results)


def challenge_8_trie():
    """Medium — Implement a Trie with insert and search_prefix."""
    class TrieNode:
        def __init__(self):
            self.children = {}
            self.is_end = False
    
    class Trie:
        def __init__(self):
            self.root = TrieNode()
        
        def insert(self, word):
            node = self.root
            for ch in word:
                if ch not in node.children:
                    node.children[ch] = TrieNode()
                node = node.children[ch]
            node.is_end = True
        
        def search(self, word):
            node = self._find_node(word)
            return node is not None and node.is_end
        
        def starts_with(self, prefix):
            return self._find_node(prefix) is not None
        
        def _find_node(self, prefix):
            node = self.root
            for ch in prefix:
                if ch not in node.children:
                    return None
                node = node.children[ch]
            return node
    
    t = Trie()
    t.insert("apple")
    checks = [
        t.search("apple") == True,
        t.search("app") == False,
        t.starts_with("app") == True,
        t.starts_with("appl") == True,
        t.search("application") == False,
        t.starts_with("banana") == False,
        t.insert("app"),
        t.search("app") == True,
    ]
    # DEBUG
    import sys as _sys
    print(f"DEBUG checks={checks} types={[type(c) for c in checks]}", file=_sys.stderr)
    return f"Trie: {sum(checks)}/{len(checks)} passed", sum(checks), len(checks)


def challenge_9_graph_bfs():
    """Medium — BFS shortest path in unweighted graph."""
    from collections import deque
    
    def shortest_path(n, edges, src, dst):
        g = [[] for _ in range(n)]
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)
        
        dist = [-1] * n
        dist[src] = 0
        q = deque([src])
        while q:
            u = q.popleft()
            if u == dst:
                return dist[u]
            for v in g[u]:
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    q.append(v)
        return -1
    
    # Graph: 0-1-2-3-4 (path) and 2-5 (branch), 0-6 (sibling)
    # 0 connects to 1 and 6
    # 1 connects to 0 and 2
    # 2 connects to 1, 3, and 5
    # 3 connects to 2 and 4
    # 4 connects to 3
    # 5 connects to 2
    # 6 connects to 0
    edges = [(0,1), (1,2), (2,3), (3,4), (2,5), (0,6)]
    tests = [
        (0, 4, 3),  # 0-1-2-3-4 = 3 steps
        (0, 0, 0),  # self = 0
        (0, 1, 1),  # direct edge = 1
        (0, 5, 2),  # 0-1-2-5 = 2 steps
        (0, 6, 1),  # direct edge = 1
        (4, 5, 2),  # 4-3-2-5 = 2 steps
    ]
    results = [shortest_path(7, edges, s, d) == exp for s, d, exp in tests]
    return f"BFS shortest path: {sum(results)}/{len(results)} passed", sum(results), len(results)


def challenge_10_heap():
    """Medium — Min-heap with insert and pop_min."""
    class MinHeap:
        def __init__(self):
            self.heap = []
        
        def _parent(self, i):
            return (i - 1) // 2
        def _left(self, i):
            return 2 * i + 1
        def _right(self, i):
            return 2 * i + 2
        
        def insert(self, val):
            self.heap.append(val)
            self._sift_up(len(self.heap) - 1)
        
        def _sift_up(self, i):
            while i > 0 and self.heap[i] < self.heap[self._parent(i)]:
                self.heap[i], self.heap[self._parent(i)] = self.heap[self._parent(i)], self.heap[i]
                i = self._parent(i)
        
        def pop_min(self):
            if not self.heap:
                return None
            min_val = self.heap[0]
            last = self.heap.pop()
            if self.heap:
                self.heap[0] = last
                self._sift_down(0)
            return min_val
        
        def _sift_down(self, i):
            n = len(self.heap)
            while True:
                smallest = i
                l = self._left(i)
                r = self._right(i)
                if l < n and self.heap[l] < self.heap[smallest]:
                    smallest = l
                if r < n and self.heap[r] < self.heap[smallest]:
                    smallest = r
                if smallest != i:
                    self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]
                    i = smallest
                else:
                    break
    
    h = MinHeap()
    for v in [5, 3, 7, 1, 9, 2, 4]:
        h.insert(v)
    
    # Should come out: 1, 2, 3, 4, 5, 7, 9
    expected = [1, 2, 3, 4, 5, 7, 9]
    results = [h.pop_min() == exp for exp in expected]
    return f"Min-heap: {sum(results)}/{len(results)} passed", sum(results), len(results)


# ─────────────────────────────────────────────────────────────
# REGISTRY
# ─────────────────────────────────────────────────────────────

CHALLENGES = [
    ("FizzBuzz", "Easy", "Warmup — 1 to 20 with Fizz/Buzz/FizzBuzz", challenge_1_fizzbuzz),
    ("Palindrome Check", "Easy", "Integer palindrome, no string conversion", challenge_2_palindrome),
    ("Binary Search", "Easy", "O(log n) search on sorted array", challenge_4_binary_search),
    ("Linked List + Cycle", "Medium", "Append, traversal, Floyd cycle detection", challenge_3_linked_list),
    ("Topological Sort", "Medium", "Kahn's algorithm for dependency ordering", challenge_5_topological_sort),
    ("LRU Cache", "Medium", "O(1) get/put with least-recently-used eviction", challenge_6_lru_cache),
    ("Longest Common Subseq", "Medium", "DP LCS — classic string algorithm", challenge_7_string_algo),
    ("Trie", "Medium", "Prefix tree with insert and starts_with", challenge_8_trie),
    ("BFS Shortest Path", "Medium", "Shortest path in unweighted graph", challenge_9_graph_bfs),
    ("Min-Heap", "Medium", "Custom min-heap with sift up/down", challenge_10_heap),
]


def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return {"runs": [], "scores": []}


def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def score_to_grade(passed, total):
    pct = passed / total if total > 0 else 0
    if pct >= 1.0:
        return "S"
    elif pct >= 0.9:
        return "A"
    elif pct >= 0.7:
        return "B"
    elif pct >= 0.5:
        return "C"
    else:
        return "D"


def run_challenge(idx, verbose=True):
    name, difficulty, desc, fn = CHALLENGES[idx]
    if verbose:
        print(f"\n{'='*60}")
        print(f"Challenge {idx+1}: {name} [{difficulty}]")
        print(f"{desc}")
        print(f"{'='*60}")
    
    start = time.perf_counter()
    try:
        output, passed, total = fn()
    except Exception as e:
        output = f"ERROR: {e}"
        passed, total = 0, 1
    elapsed = time.perf_counter() - start
    
    grade = score_to_grade(passed, total)
    pct = (passed / total * 100) if total > 0 else 0
    
    if verbose:
        print(f"Result: {passed}/{total} tests ({pct:.0f}%) — Grade: {grade}")
        print(f"Time: {elapsed*1000:.1f}ms")
        print(f"Output: {output[:300]}")
    
    return {
        "idx": idx,
        "name": name,
        "difficulty": difficulty,
        "passed": passed,
        "total": total,
        "pct": round(pct, 1),
        "grade": grade,
        "time_ms": round(elapsed * 1000, 1),
        "ts": datetime.now(timezone.utc).isoformat(),
    }


def show_history():
    history = load_history()
    runs = history.get("runs", [])
    if not runs:
        print("No challenge history yet. Run with --challenge or --practice")
        return
    
    print(f"\n{'='*60}")
    print(f"CODING CHALLENGE HISTORY — {len(runs)} total runs")
    print(f"{'='*60}")
    
    # Group by challenge
    by_challenge = {}
    for r in runs:
        key = r["name"]
        if key not in by_challenge:
            by_challenge[key] = []
        by_challenge[key].append(r)
    
    print(f"\n{'Challenge':<25} {'Runs':>4} {'Best':>4} {'Avg':>6} {'Recent':>30}")
    print("-" * 80)
    for name, rs in sorted(by_challenge.items(), key=lambda x: -len(x[1])):
        best = max(r["pct"] for r in rs)
        avg = statistics.mean(r["pct"] for r in rs)
        recent = rs[-1]["ts"][:16]
        print(f"{name:<25} {len(rs):>4} {best:>3.0f}%  {avg:>5.1f}%  {recent}")
    
    # Overall trend
    if len(runs) >= 5:
        recent_5 = runs[-5:]
        older = runs[-10:-5] if len(runs) >= 10 else runs[:5]
        recent_avg = statistics.mean(r["pct"] for r in recent_5)
        older_avg = statistics.mean(r["pct"] for r in older)
        delta = recent_avg - older_avg
        print(f"\nOverall trend (last 5 vs prior 5): {'+' if delta >= 0 else ''}{delta:.1f}%")


def log_to_execution(output, challenge_name, passed, total):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n### {ts}\n**Command:** `python3 scripts/coding_challenge.py --challenge N`\n**Challenge:** {challenge_name}\n**Result:** {passed}/{total} — {output}\n---\n"
    with open(LOG_FILE, "a") as f:
        f.write(entry)


def main():
    args = sys.argv[1:]
    
    if "--list" in args:
        print(f"\n{'='*60}")
        print(f"CODING CHALLENGES — {len(CHALLENGES)} challenges")
        print(f"{'='*60}")
        for i, (name, diff, desc, _) in enumerate(CHALLENGES):
            print(f"  [{i+1}] {name:<25} [{diff}] {desc}")
        print(f"\nDifficulty: Easy (4) | Medium (6)")
        return
    
    if "--history" in args:
        show_history()
        return
    
    history = load_history()
    
    # Run specific challenge
    for i, arg in enumerate(args):
        if arg == "--challenge" and i + 1 < len(args):
            idx = int(args[i + 1]) - 1
            if 0 <= idx < len(CHALLENGES):
                result = run_challenge(idx)
                history["runs"].append(result)
                save_history(history)
                log_to_execution(f"{result['pct']}% ({result['passed']}/{result['total']})", 
                               result["name"], result["passed"], result["total"])
                return
            else:
                print(f"Invalid challenge number. 1-{len(CHALLENGES)}")
                return
    
    # Practice mode: run 5 random challenges
    if "--practice" in args:
        selected = random.sample(range(len(CHALLENGES)), min(5, len(CHALLENGES)))
        print(f"\n🎯 PRACTICE MODE — Running {len(selected)} random challenges\n")
        results = []
        for idx in selected:
            result = run_challenge(idx)
            results.append(result)
            history["runs"].append(result)
            save_history(history)
        
        total_passed = sum(r["passed"] for r in results)
        total_tests = sum(r["total"] for r in results)
        avg_time = statistics.mean(r["time_ms"] for r in results)
        grades = [r["grade"] for r in results]
        
        print(f"\n{'='*60}")
        print(f"PRACTICE SUMMARY")
        print(f"{'='*60}")
        print(f"Overall: {total_passed}/{total_tests} ({total_passed/total_tests*100:.0f}%)")
        print(f"Avg time: {avg_time:.1f}ms")
        print(f"Grades: {' '.join(grades)}")
        print(f"Score: {sum(ord(g) for g in grades)}/{len(grades) * ord('S')}")
        return
    
    # Default: run all challenges
    print(f"\n{'='*60}")
    print(f"FULL CHALLENGE SUITE — Running all {len(CHALLENGES)} challenges")
    print(f"{'='*60}")
    
    results = []
    for idx in range(len(CHALLENGES)):
        result = run_challenge(idx)
        results.append(result)
        history["runs"].append(result)
        save_history(history)
    
    # Summary
    easy = [r for r in results if r["difficulty"] == "Easy"]
    medium = [r for r in results if r["difficulty"] == "Medium"]
    
    def avg_pct(rs):
        return statistics.mean(r["pct"] for r in rs) if rs else 0
    
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Easy:   {avg_pct(easy):.1f}% avg  ({sum(r['passed'] for r in easy)}/{sum(r['total'] for r in easy)})")
    print(f"Medium: {avg_pct(medium):.1f}% avg  ({sum(r['passed'] for r in medium)}/{sum(r['total'] for r in medium)})")
    all_passed = sum(r["passed"] for r in results)
    all_total = sum(r["total"] for r in results)
    print(f"Total:  {all_passed}/{all_total} ({all_passed/all_total*100:.1f}%)")
    print(f"\nHistory saved to: {HISTORY_FILE}")
    print(f"Run --history to see trends")


if __name__ == "__main__":
    main()
