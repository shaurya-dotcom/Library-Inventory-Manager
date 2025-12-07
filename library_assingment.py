import json
import logging
import os

# simple logging setup (file ban jayega same folder me)
logging.basicConfig(
    filename="library_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class Book:
    # ek book ka data store karne ke liye simple class
    def __init__(self, title, author, isbn, status="available"):
        self.title = title
        self.author = author
        self.isbn = isbn
        # available ya issued
        self.status = status

    def to_dict(self):
        # json file me save karne ke liye dict bana raha hu
        return {
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "status": self.status
        }

    @staticmethod
    def from_dict(data):
        # json se wapas Book object
        return Book(
            data.get("title", ""),
            data.get("author", ""),
            data.get("isbn", ""),
            data.get("status", "available")
        )

    def __str__(self):
        return f"{self.title} - {self.author} (ISBN: {self.isbn}) [{self.status}]"


class LibraryInventory:
    # pura library ka kaam yaha pe hoga
    def __init__(self, file_name="catalog.json"):
        self.file_name = file_name
        self.books = []
        self.load_data()

    def load_data(self):
        """Json file se data load kar raha hu."""
        if not os.path.exists(self.file_name):
            # file pehli baar banegi
            self.books = []
            logging.warning("Catalog file not found, starting with empty list")
            return

        try:
            with open(self.file_name, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.books = [Book.from_dict(item) for item in data]
            logging.info(f"Loaded {len(self.books)} books from file")
        except json.JSONDecodeError:
            # agar file corrupt ho gayi ho
            self.books = []
            logging.error("JSON decode error, starting with empty list")
        except Exception as e:
            self.books = []
            logging.error(f"Error while reading file: {e}")

    def save_data(self):
        """Books list ko json file me save kar raha hu."""
        try:
            data = [b.to_dict() for b in self.books]
            with open(self.file_name, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            logging.info(f"Saved {len(self.books)} books to file")
        except Exception as e:
            logging.error(f"Error while saving file: {e}")

    def add_book(self, title, author, isbn):
        # pehle check kar raha hu ki isbn already exist to nahi karta
        for b in self.books:
            if b.isbn == isbn:
                logging.warning(f"Duplicate ISBN tried: {isbn}")
                return False

        new_book = Book(title, author, isbn)
        self.books.append(new_book)
        self.save_data()
        logging.info(f"Book added: {title} ({isbn})")
        return True

    def find_by_isbn(self, isbn):
        for b in self.books:
            if b.isbn == isbn:
                return b
        return None

    def search_by_title(self, keyword):
        keyword = keyword.lower()
        result = []
        for b in self.books:
            if keyword in b.title.lower():
                result.append(b)
        logging.info(f"Search by title '{keyword}' found {len(result)} result(s)")
        return result

    def issue_book(self, isbn):
        book = self.find_by_isbn(isbn)
        if book is None:
            logging.warning(f"Issue failed, book not found: {isbn}")
            return False, "Book not found."

        if book.status == "issued":
            logging.warning(f"Issue failed, already issued: {isbn}")
            return False, "Book is already issued."

        book.status = "issued"
        self.save_data()
        logging.info(f"Book issued: {isbn}")
        return True, "Book issued successfully."

    def return_book(self, isbn):
        book = self.find_by_isbn(isbn)
        if book is None:
            logging.warning(f"Return failed, book not found: {isbn}")
            return False, "Book not found."

        if book.status == "available":
            logging.warning(f"Return failed, already available: {isbn}")
            return False, "Book was not issued."

        book.status = "available"
        self.save_data()
        logging.info(f"Book returned: {isbn}")
        return True, "Book returned successfully."

    def show_all_books(self):
        return self.books


# ================= MENU FUNCTIONS ===================

def print_menu():
    print("\n==== Library Management System ====")
    print("1. Add Book")
    print("2. Issue Book")
    print("3. Return Book")
    print("4. View All Books")
    print("5. Search Book")
    print("6. Exit")


def get_choice():
    while True:
        try:
            ch = int(input("Enter your choice (1-6): "))
            if 1 <= ch <= 6:
                return ch
            else:
                print("Please enter number between 1 and 6.")
        except ValueError:
            # agar user ne number nahi dala
            print("Invalid input, please enter a number.")


def add_book_flow(inv):
    print("\n--- Add Book ---")
    title = input("Enter title: ").strip()
    author = input("Enter author name: ").strip()
    isbn = input("Enter ISBN: ").strip()

    if title == "" or author == "" or isbn == "":
        print("All fields are compulsory.")
        return

    ok = inv.add_book(title, author, isbn)
    if ok:
        print("Book added successfully.")
    else:
        print("Book with this ISBN already exists.")


def issue_book_flow(inv):
    print("\n--- Issue Book ---")
    isbn = input("Enter ISBN to issue: ").strip()
    if isbn == "":
        print("ISBN cannot be empty.")
        return
    success, msg = inv.issue_book(isbn)
    print(msg)


def return_book_flow(inv):
    print("\n--- Return Book ---")
    isbn = input("Enter ISBN to return: ").strip()
    if isbn == "":
        print("ISBN cannot be empty.")
        return
    success, msg = inv.return_book(isbn)
    print(msg)


def view_all_flow(inv):
    print("\n--- All Books ---")
    books = inv.show_all_books()
    if len(books) == 0:
        print("No books in library yet.")
        return
    for i, b in enumerate(books, start=1):
        print(f"{i}. {b}")


def search_book_flow(inv):
    print("\n--- Search Book ---")
    print("1. Search by Title")
    print("2. Search by ISBN")

    try:
        ch = int(input("Enter your choice (1-2): "))
    except ValueError:
        print("Invalid input.")
        return

    if ch == 1:
        key = input("Enter title keyword: ").strip()
        if key == "":
            print("Keyword cannot be empty.")
            return
        res = inv.search_by_title(key)
        if len(res) == 0:
            print("No books found.")
        else:
            print(f"Found {len(res)} book(s):")
            for b in res:
                print(b)
    elif ch == 2:
        isbn = input("Enter ISBN: ").strip()
        if isbn == "":
            print("ISBN cannot be empty.")
            return
        b = inv.find_by_isbn(isbn)
        if b is None:
            print("No book found.")
        else:
            print("Book found:")
            print(b)
    else:
        print("Wrong choice.")


def main():
    logging.info("Program started")
    inv = LibraryInventory()

    while True:
        print_menu()
        choice = get_choice()

        if choice == 1:
            add_book_flow(inv)
        elif choice == 2:
            issue_book_flow(inv)
        elif choice == 3:
            return_book_flow(inv)
        elif choice == 4:
            view_all_flow(inv)
        elif choice == 5:
            search_book_flow(inv)
        elif choice == 6:
            print("Exiting program...")
            logging.info("Program exited by user")
            break


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # last level safety, agar koi unexpected error aa jaye
        logging.error(f"Unexpected error: {e}")
        print("Some error happened, please check log file.")
