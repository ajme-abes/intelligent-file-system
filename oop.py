# class Employee:
#     employ_numbers = 0
#     raise_amount = 1.50
#     def __init__(self, fname, lname, pay):
#         self.fname = fname
#         self.lname = lname
#         self.pay = pay
#         self.email = fname + '.' + lname + '@company.com'
#         Employee.employ_numbers += 1
#     def fullname(self):
#         return f'fullName: {self.fname} {self.lname}'

#     def apply_amount(self):
#         self.pay = int(self.pay * self.raise_amount)
#     @classmethod
#     def set_raise_amount(cls, amount):
#         cls.raise_amount = amount
    
#     @classmethod
#     def str_sep(cls,emp_str):
#         fname, lname, pay = emp_str.split('-')
#         return cls(fname,lname,pay)

#     @staticmethod
#     def is_workdays(day):
#         if day.weekday() == 5 or day.weekday() == 5:
#             return False
#         return True
# class Manager(Employee):
#     def __init__(self, fname, lname, pay,employees=None):
#         super().__init__(fname,lname,pay)
#         if employees is None:
#             self.employees = []
#         else:
#             self.employees = employees
#     def add_empl(self, emp):
#         if emp not in self.employees:
#             self.employees.append(emp)

#     def display_empo(self):
#         for emp in self.employees:
#             print(f" {self.fullname()}")
#     def total_empl(self):
#         total = len(self.employees)
#         print(f"total employee: {total}")
#         return total


# mgr1 = Manager("ajmel", "abes", 5000)
# emp_a = Employee("John", "Doe", 3000)
# emp_b = Employee("Jane", "Smith", 4000)
# emp_c = Employee("Mike", "Jordan", 3500)

# # 3. Add each one to the manager
# mgr1.add_empl(emp_a)
# mgr1.add_empl(emp_b)
# mgr1.add_empl(emp_c)


# print(mgr1.total_empl())
# class Book:
#     def __init__(self, title, author):
#         self.title = title
#         self.author = author
# class Libarary:
#     def __init__(self):
#         self.books = []
#     def add_books(self, book):
#       self.books.append(book)
#     def display_book(self):
#         for book in self.books:
#             print(f"book: {book.title} by {book.author}")


# library = Libarary()
# library.add_books(Book(input("title:"), input("author:")))
# library.add_books(Book("limitless", "jimkiwik"))
# library.add_books(Book("think and grow rich", "robert Green"))
# library.display_book()

class Electronics:
    def __init__(self, name, modelz, year):
        self.name = name
        self.model = model
        self.year = year


