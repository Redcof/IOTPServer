from S4Crypto.S4Hash import s4hash

print "ce4d82bf5d688c9e1758fe00f7d5244b" == s4hash("sir.surojit")
print "d241c457b959370b97ba2a2fc6ed6314" == s4hash("123456")
print "Token: " + s4hash(s4hash("sir.surojit") + s4hash("123456"))
