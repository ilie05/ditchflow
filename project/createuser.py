import stdiomask

password = stdiomask.getpass()
confirm_pass = stdiomask.getpass(prompt="Confirm password: ")

print(password)
print(confirm_pass)
