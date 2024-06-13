from http.server import BaseHTTPRequestHandler
from urllib import parse
import json
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        s = self.path
        url_component = parse.urlsplit(s)
        query_string_list = parse.parse_qsl(url_component.query)
        my_dic = dict(query_string_list)

        if "category" in my_dic:
            self.get_questions_by_category(my_dic)
        else:
            self.get_questions_by_amount(my_dic)

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

        req = requests.get(url)
        rec_question = req.json()
        output = []
        num = 1
        for item in rec_question["results"]:
            question = item["question"]
            correct_answer = item["correct_answer"]
            cat = item["category"]
            output.append({
                "question number": num,
                "question": question,
                "answer": correct_answer,
                "category": cat
            })
            num += 1

        # Send HTTP status 200 (OK)
        self.send_response(200)

        # Set the Content-type to 'application/json'
        self.send_header("Content-type", "application/json")

        # End headers
        self.end_headers()

        # Write the output to the response
        self.wfile.write(json.dumps(output).encode())
        return

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

        req = requests.get(url)
        rec_question = req.json()

        # Validate the response from the API
        if rec_question["response_code"] != 0:
            self.send_response(400)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write("Invalid request to the trivia API.".encode())
            return

        output = ""
        num = 1
        for item in rec_question["results"]:
            question = item["question"]
            correct_answer = item["correct_answer"]
            cat = item["category"]
            output += f"Category: {cat}\nQuestion number: {num}\nQuestion: {question}\nAnswer: {correct_answer}\n\n"
            num += 1

        # Send HTTP status 200 (OK)
        self.send_response(200)

        # Set the Content-type to 'text/plain'
        self.send_header("Content-type", "text/plain")

        # End headers
        self.end_headers()

        # Write the output to the response
        self.wfile.write(output.encode())
        return
