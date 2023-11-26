import re
string = "Description:"
pattern = "[\u4e00-\ufaff]\s|[\u4e00-\ufaff]\s+|[\u4e00-\ufaff]\t"
pattern += "|[\u3040-\u309F]\s|[\u3040-\u309F]\s+|[\u3040-\u309F]\t" #hiragana
pattern += "|[\u30A0-\u30ff]\s|[\u30A0-\u30ff]\s+|[\u30A0-\u30ff]\t"
pattern += "|[\u4e00-\u9fff]\s|[\u4e00-\u9fff]\s+|[\u4e00-\u9fff]\t"
pattern = re.compile(pattern)
pattern2 = re.compile("[0-9]+|[a-zA-Z]+\'*[a-z]*")
pattern = pattern.findall(string)
pattern2 = pattern2.findall(string)
# string = string.replace("[\u4e00-\ufaff]\s", "")
print(pattern)
print(pattern2)