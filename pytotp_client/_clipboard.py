import subprocess  # nosec


def write_to_clipboard(output: str) -> None:
    process = subprocess.Popen("pbcopy", env={"LANG": "en_US.UTF-8"}, stdin=subprocess.PIPE)  # nosec
    process.communicate(output.encode("utf-8"))
