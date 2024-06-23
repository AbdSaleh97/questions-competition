from http.server import BaseHTTPRequestHandler
from urllib import parse
import json
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            s = self.path
            url_component = parse.urlsplit(s)
            query_string_list = parse.parse_qsl(url_component.query)
            my_dic = dict(query_string_list)

            if "category" in my_dic:
                self.get_questions_by_category(my_dic)
            else:
                self.get_questions_by_amount(my_dic)
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def get_questions_by_amount(self, my_dic):
        amount = my_dic.get("amount", "20")  # Default to 20 if no amount provided

        # Ensure the amount does not exceed 50
        try:
            amount = int(amount)
            if amount > 50:
                amount = 50
        except ValueError:
            amount = 20  # Default to 20 if invalid number provided

        url = f"https://opentdb.com/api.php?amount={amount}"

        try:
            req = requests.get(url)
            req.raise_for_status()
            rec_question = req.json()
        except requests.RequestException as e:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
            return

        output = []
        for num, item in enumerate(rec_question["results"], start=1):
            question = item["question"]
            correct_answer = item["correct_answer"]
            cat = item["category"]
            output.append({
                "question number": num,
                "question": question,
                "answer": correct_answer,
                "category": cat
            })

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(output).encode())

    def get_questions_by_category(self, my_dic):
        category = my_dic.get("category", "")
        amount = 10  # Fixed to 10 questions

        # Ensure the category is a valid integer and within the valid range
        try:
            category = int(category)
            if category < 9 or category > 32:
                raise ValueError("Invalid category")
        except ValueError:
            self.send_response(400)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write("Invalid category. Category must be between 9 and 32.".encode())
            return

        url = f"https://opentdb.com/api.php?amount={amount}&category={category}"

        try:
            req = requests.get(url)
            req.raise_for_status()
            rec_question = req.json()
        except requests.RequestException as e:
            self.send_response(500)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(f"Error fetching data: {e}".encode())
            return

        if rec_question["response_code"] != 0:
            self.send_response(400)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write("Invalid request to the trivia API.".encode())
            return

        output = ""
        for num, item in enumerate(rec_question["results"], start=1):
            question = item["question"]
            correct_answer = item["correct_answer"]
            cat = item["category"]
            output += f"Category: {cat}\nQuestion number: {num}\nQuestion: {question}\nAnswer: {correct_answer}\n\n"

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(output.encode())

if __name__ == "__main__":
    from http.server import HTTPServer
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, handler)
    print("Server running on port 8000")
    httpd.serve_forever()
