import pypdf
import json
import re
# PDF = "UP09114825_2083O24353S6D57774E2.html.pdf"
# JSON = "24s2.json"

def get_marks(pdf,shift):
    reader= pypdf.PdfReader(pdf)
    with open(f"keys/{shift}.json", "r") as f:
        data = json.load(f)

    #data.get()
    #print(reader.pages[0].extract_text())




    def extract_answered_questions(raw_text):
        blocks = re.split(r'Q\.(\d+)', raw_text)
        questions = {}

        for i in range(1, len(blocks), 2):
            q_num = int(blocks[i])
            content = blocks[i+1]

            # Status
            status_match = re.search(r'Status\s*:(.*)', content)
            status = status_match.group(1).strip() if status_match else None

            if status != "Answered":
                continue

            # Common fields
            qid = re.search(r'Question ID\s*:(\d+)', content)
            qtype = re.search(r'Question Type\s*:(.*)', content)

            qid = qid.group(1) if qid else None
            qtype = qtype.group(1).strip() if qtype else None

            # 👉 MCQ handling
            if qtype == "MCQ":
                chosen = re.search(r'Chosen Option\s*:(\S+)', content)
                option_ids = re.findall(r'Option \d+ ID\s*:(\d+)', content)

                chosen = chosen.group(1) if chosen else None

                selected_option_id = None
                if chosen and chosen.isdigit():
                    idx = int(chosen) - 1
                    if 0 <= idx < len(option_ids):
                        selected_option_id = option_ids[idx]

                questions[q_num] = {
                    "question_id": qid,
                    "question_type": qtype,
                    "chosen_option": int(chosen) if chosen and chosen.isdigit() else None,
                    "option_ids": option_ids,
                    "selected_option_id": selected_option_id
                }

            # 👉 SA (integer answer)
            elif qtype == "SA":
                ans_match = re.search(r'Answer\s*:\s*(\S+)', content)
                ans = ans_match.group(1) if ans_match else None

                # convert to int safely
                try:
                    ans = int(ans)
                except:
                    ans = None

                questions[q_num] = {
                    "question_id": qid,
                    "question_type": qtype,
                    "answer": ans
                }

        return questions
    text = ""
    for page in reader.pages:
        text+=page.extract_text()

    questions = extract_answered_questions(text)

    math_marks = physics_marks = chemistry_marks = 0

    math_correct = math_wrong = 0
    physics_correct = physics_wrong = 0
    chemistry_correct = chemistry_wrong = 0

    for q_num, q in questions.items():

        # MCQ
        if q['question_type'] == "MCQ":
            correct = data.get(q['question_id'])

            if q['selected_option_id'] == correct:
                if q_num <= 25:
                    math_marks += 4
                elif 25<q_num <= 50:
                    physics_marks += 4
                elif 50<q_num<=75:
                    chemistry_marks += 4
            else:
                if q_num <= 25:
                    math_marks -= 1
                elif 25<q_num <= 50:
                    physics_marks -= 1
                elif 50<q_num<=75:
                    chemistry_marks -= 1

        # SA (integer)
        elif q['question_type'] == "SA":
            correct = data.get(q['question_id'])

            if q['answer'] == int(correct):
                if q_num <= 25:
                    math_marks += 4
                elif 25<q_num <= 50:
                    physics_marks += 4
                elif 50<q_num<=75:
                    chemistry_marks += 4
            else:
                if q_num <= 25:
                    math_marks -= 1
                elif 25<q_num <= 50:
                    physics_marks -= 1
                elif 50<q_num<=75:
                    chemistry_marks -= 1


    marks = math_marks + physics_marks + chemistry_marks

    return {'marks':marks,"math_marks":math_marks,'physics_marks':physics_marks,'chemistry_marks':chemistry_marks}


    