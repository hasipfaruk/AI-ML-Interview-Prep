# 14 — DSA Coding Round (for AI/ML roles)

Most ML/AI engineer loops include 1–2 standard coding rounds (LeetCode-style, usually medium).
You don't need 500 problems — you need the **~15 patterns**. Learn the pattern, then do 5–8 problems each.

## The method for every coding question (say it out loud)
1. **Clarify:** input size, types, edge cases (empty, duplicates, negatives), return format.
2. **Example:** walk through a small example by hand.
3. **Brute force first:** state it and its complexity.
4. **Optimize:** which pattern fits? State new complexity.
5. **Code** cleanly with good names.
6. **Test:** run your example + edge cases by hand.
7. **Complexity:** time and space.

## Patterns → when to use → classic problems

| # | Pattern | Signal in the question | Practice problems |
|---|---------|------------------------|-------------------|
| 1 | **Hash map / set** | "find pair", "count", "seen before", O(1) lookup | Two Sum, Group Anagrams, Longest Consecutive Sequence |
| 2 | **Two pointers** | sorted array, pairs, palindrome, in-place | 3Sum, Container With Most Water, Valid Palindrome |
| 3 | **Sliding window** | contiguous subarray/substring, "longest/shortest with condition" | Longest Substring Without Repeating, Minimum Window Substring |
| 4 | **Prefix sum** | range sums, "subarray sum equals k" | Subarray Sum Equals K, Range Sum Query |
| 5 | **Binary search** | sorted data, "minimum X such that…", search on answer | Search in Rotated Array, Koko Eating Bananas, Median of Two Sorted Arrays |
| 6 | **Stack / monotonic stack** | matching brackets, "next greater element" | Valid Parentheses, Daily Temperatures, Largest Rectangle in Histogram |
| 7 | **Heap / priority queue** | top-k, k-th largest, merge sorted, streaming median | Kth Largest, Top K Frequent, Merge K Sorted Lists, Find Median from Data Stream |
| 8 | **Linked list** | reverse, cycle, merge | Reverse List, Linked List Cycle, LRU Cache (hash map + doubly linked list) |
| 9 | **Trees (DFS/BFS)** | hierarchy, depth, paths | Max Depth, Level Order, Validate BST, Lowest Common Ancestor, Serialize Tree |
| 10 | **Graphs (BFS/DFS/union-find/topological sort)** | grid, connections, dependencies, shortest path | Number of Islands, Course Schedule, Clone Graph, Dijkstra (Network Delay Time) |
| 11 | **Backtracking** | "all combinations/permutations/subsets" | Subsets, Permutations, Combination Sum, Word Search |
| 12 | **Dynamic programming** | "number of ways", "min/max", overlapping subproblems | Climbing Stairs, Coin Change, Longest Increasing Subsequence, Edit Distance, LCS |
| 13 | **Greedy / intervals** | scheduling, merge intervals | Merge Intervals, Meeting Rooms II, Jump Game |
| 14 | **Trie** | prefix search, autocomplete | Implement Trie, Word Search II |
| 15 | **Bit manipulation / math** | XOR tricks, powers | Single Number, Counting Bits |

**ML-flavored coding questions (common at AI companies):** Edit distance (NLP), LRU cache (model cache), top-k frequent words, reservoir sampling, matrix ops, implement tokenizer, rate limiter, moving average from a stream, merge k sorted lists (merge search results), autocomplete with trie, sample from a weighted distribution (prefix sums + binary search).

## Complexity cheat sheet
| Operation | Complexity |
|---|---|
| Hash map get/put | O(1) avg |
| Sort | O(n log n) |
| Binary search | O(log n) |
| Heap push/pop | O(log n); build heap O(n) |
| BFS/DFS | O(V + E) |
| Top-k with heap | O(n log k) |
| Recursion space | O(depth) |

Rough limits: n ≤ 10⁵ → need O(n log n) or better. n ≤ 10³ → O(n²) ok. n ≤ 20 → exponential/backtracking ok.

## Python templates
```python
# Sliding window (variable size)
def longest_unique_substring(s):
    seen, left, best = {}, 0, 0
    for right, ch in enumerate(s):
        if ch in seen and seen[ch] >= left:
            left = seen[ch] + 1
        seen[ch] = right
        best = max(best, right - left + 1)
    return best

# Binary search on answer
def min_feasible(lo, hi, ok):            # smallest x in [lo, hi] with ok(x) True
    while lo < hi:
        mid = (lo + hi) // 2
        if ok(mid): hi = mid
        else: lo = mid + 1
    return lo

# BFS on grid
from collections import deque
def bfs(grid, start):
    R, C = len(grid), len(grid[0])
    q, seen = deque([start]), {start}
    while q:
        r, c = q.popleft()
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and (nr, nc) not in seen and grid[nr][nc] != '#':
                seen.add((nr, nc)); q.append((nr, nc))
    return seen

# Top-k with heap
import heapq
from collections import Counter
def top_k_frequent(nums, k):
    return [x for x, _ in heapq.nlargest(k, Counter(nums).items(), key=lambda t: t[1])]

# LRU cache
from collections import OrderedDict
class LRUCache:
    def __init__(self, cap): self.cap, self.d = cap, OrderedDict()
    def get(self, k):
        if k not in self.d: return -1
        self.d.move_to_end(k); return self.d[k]
    def put(self, k, v):
        self.d[k] = v; self.d.move_to_end(k)
        if len(self.d) > self.cap: self.d.popitem(last=False)

# DP: edit distance
def edit_distance(a, b):
    dp = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        prev, dp[0] = dp[0], i
        for j in range(1, len(b) + 1):
            cur = dp[j]
            dp[j] = prev if a[i-1] == b[j-1] else 1 + min(prev, dp[j], dp[j-1])
            prev = cur
    return dp[-1]
```

## 8-week plan
| Weeks | Patterns | Daily |
|---|---|---|
| 1–2 | 1–4 (hash, pointers, window, prefix) | 2 problems |
| 3–4 | 5–9 (binary search, stack, heap, lists, trees) | 2 problems |
| 5–6 | 10–12 (graphs, backtracking, DP) | 2 problems |
| 7–8 | 13–15 + mixed timed sets | 1 timed mock (45 min, 2 problems) |
Use a curated list (e.g., "NeetCode 150" / "Blind 75") — it covers these patterns.
