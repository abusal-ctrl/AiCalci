import statistics
import re


def statistics_tool(expression: str) -> str:
    """
    Expects a comma-separated list of numbers, e.g. "1, 2, 3, 4, 5".
    Returns mean, median, mode, stdev.
    """
    nums = [float(n) for n in re.findall(r"-?\d+\.?\d*", expression)]
    if not nums:
        raise ValueError("No numbers found for statistics.")
    return (
        f"mean={statistics.mean(nums)}, "
        f"median={statistics.median(nums)}, "
        f"mode={statistics.mode(nums) if len(set(nums)) < len(nums) else 'N/A'}, "
        f"stdev={statistics.pstdev(nums):.4f}"
    )