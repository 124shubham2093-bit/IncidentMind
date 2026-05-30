import subprocess

result = subprocess.run(
    [
        r"C:\Users\Prakash PC\Desktop\coral\coral.exe",
        "source",
        "list"
    ],
    capture_output=True,
    text=True
)

print(result.stdout)