"""This module define GitVersion class."""

import re
import shutil
import subprocess
from importlib.metadata import version as prodcut_version
from importlib.resources import as_file
from importlib.resources import files
from pathlib import Path


class GitVersion:
    """Class to manage git operations."""

    @classmethod
    def _execute(cls, args: list[str]) -> str:
        out = subprocess.run(
            args=args, capture_output=True, text=True, check=True
        ).stdout.strip()
        return out

    @classmethod
    def package_name(cls) -> str:
        """Return the package name."""
        origin_path = Path(__file__)
        parents = origin_path.parents
        package_name = origin_path.name
        is_package_found = False
        for parent in parents:
            if parent.name in ["src", "site-packages"]:
                is_package_found = True
                break
            else:
                package_name = parent.name
        if not is_package_found:
            raise RuntimeError(
                "Package directory should be within `src` "
                + "or `site-packages` directory."
            )
        return package_name

    @classmethod
    def is_product(cls) -> bool:
        """Check if the package is a product."""
        package_name = cls.package_name()
        traverse = files(package_name)
        context_manager = as_file(traverse)
        with context_manager as path:
            package_path = Path(path)
        parent = package_path.parent.name
        if parent == "site-packages":
            is_product = True
        else:
            is_product = False
        return is_product

    @classmethod
    def git_available(cls) -> bool:
        """Check if git is available in the system."""
        path = shutil.which("git")
        return path is not None

    @classmethod
    def version(cls) -> str:
        """Return the current git version."""
        version = "unknown"
        if cls.is_product():
            version = cls._version_from_metadata()
        if version == "unknown" and cls.git_available():
            out = cls._execute(["git", "describe", "--tags", "--dirty"])
            describes = out.split("-")
            semantic_version = re.sub(r"^v", "", describes[0])
            if len(describes) == 1:
                commit_count = 0
                commit_hash = ""
                is_dirty = False
            if len(describes) == 2:
                commit_count = 0
                commit_hash = ""
                is_dirty = describes[-1] == "dirty"
            else:
                commit_count = int(describes[1])
                commit_hash = re.sub(r"^g", "", describes[2])
                is_dirty = describes[-1] == "dirty"
            major, minor, patch = semantic_version.split(".")
            if commit_count == 0 and not is_dirty:
                version = f"{major}.{minor}.{patch}"
            elif is_dirty:
                version = (
                    f"{major}.{minor}.{patch}"
                    + f".post{commit_count}.dev0+{commit_hash}"
                )
            else:
                version = (
                    f"{major}.{minor}.{patch}"
                    + f".post{commit_count}+{commit_hash}"
                )
        return version

    @classmethod
    def current_branch(cls) -> str:
        """Return the current git branch."""
        out = cls._execute(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        return out

    @classmethod
    def last_commit_message(cls) -> str:
        """Return the last commit message."""
        out = cls._execute(["git", "log", "-1", "--pretty=%B"])
        return out

    @classmethod
    def delete_tag(cls, tag: str) -> None:
        """Delete a git tag."""
        cls._execute(["git", "tag", "-d", tag])

    @classmethod
    def add_tag(cls, tag: str, message: str = "") -> None:
        """Add a git tag."""
        if message:
            args = ["git", "tag", "-a", tag, "-m", message]
        else:
            args = ["git", "tag", tag]
        cls._execute(args)

    @classmethod
    def add_file(cls, file_name: str) -> None:
        """Add a file to git."""
        cls._execute(["git", "add", file_name])

    @classmethod
    def push(cls, verify: bool = True) -> None:
        """Push changes to git."""
        if verify:
            args = ["git", "push"]
        else:
            args = ["git", "push", "--no-verify"]
        cls._execute(args)

    @classmethod
    def push_tags(cls) -> None:
        """Push tags to git."""
        cls._execute(["git", "push", "--tags"])

    @classmethod
    def commit(
        cls, message: str, verify: bool = True, allow_empty: bool = False
    ) -> None:
        """Commit changes to git."""
        if allow_empty:
            args = ["git", "commit", "--allow-empty", "-m", message]
        else:
            args = ["git", "commit", "-m", message]
        if not verify:
            args.append("--no-verify")
        cls._execute(args)

    @classmethod
    def release(cls) -> None:
        """Release the current version."""
        if current_branch := cls.current_branch() != "main":
            raise RuntimeError(
                f"Your current branch is '{current_branch}'. "
                "Release can only be performed from the 'main' branch."
            )
        version = cls.version()
        if version == "unknown":
            raise RuntimeError("Cannot release: version is unknown.")
        if "dev0" in version:
            raise RuntimeError(
                "Cannot release: version is a development version."
            )
        if "post" in version:
            raise RuntimeError(
                "Cannot release: version is a post-release version."
            )
        cls.delete_tag("v" + version)
        cls.commit(f"Release v{version}", verify=False, allow_empty=True)
        cls.add_tag("v" + version)
        cls.push_tags()
        cls.push(verify=False)

    @classmethod
    def build(cls) -> None:
        """Build the package."""
        if current_branch := cls.current_branch() != "main":
            raise RuntimeError(
                f"Your current branch is '{current_branch}'. "
                "Release can only be performed from the 'main' branch."
            )
        last_commit_message = cls.last_commit_message()
        if not last_commit_message.startswith("Release v"):
            raise RuntimeError(
                "Cannot build: repository is not in a release state."
            )
        cls._execute(["uv", "build"])

    @classmethod
    def _version_from_metadata(cls) -> str:
        """Get the version from the package metadata."""
        package_name = cls.package_name()
        try:
            version = prodcut_version(package_name)
        except Exception as e:
            version = "unknown"
        return version
