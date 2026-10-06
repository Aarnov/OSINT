from modules.scanner import run_email_scan


email = "aarnoadhikari123@gmail.com"

result = run_email_scan(email)

print("Success:", result["success"])
print("Scan ID:", result["scan_id"])

if result["success"]:
    print("JSON successfully loaded.")
    print("Data type:", type(result["data"]))

else:
    print("Scanner failed:")
    print(result["error"])