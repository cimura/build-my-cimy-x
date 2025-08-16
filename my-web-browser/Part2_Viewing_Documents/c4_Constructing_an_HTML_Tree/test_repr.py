class Person:
	def __init__(self, name="taro", age=42):
		self.name = name
		self.age = age

	def __repr__(self):
		return f"名前は{self.name}, 年齢は{self.age}"

hanako = Person("Hanako", 21)
print(hanako)

nanashi = Person()
print(nanashi)