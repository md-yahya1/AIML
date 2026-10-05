from git_tools import git_status


status = git_status()

if status:
    print("Changes detected:")
    print(status)
else:
    print("Working tree is clean.")