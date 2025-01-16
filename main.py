# kindle_api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import re

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","https://zindex-zyn.vercel.app","https://www.z-index.org","https://z-index.org","exp://10.0.0.153:8081"],  # Your React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define data models 
class KindleContent(BaseModel):
    content: str


def process_kindle_notes(content: str) -> dict:
    books = {}
    sections = content.split('==========')
    seen = set()
    # print(sections)

    pattern = r'(?:Location|位置)\s*#?(\d+(?:-\d+)?)'
    def get_location_numbers(loc_str):
        # Extract and convert location numbers to integers
        match = re.search(pattern, loc_str)
        if match:
            numbers = match.group(1).split('-')
            return (int(numbers[0]), int(numbers[1]) if len(numbers) > 1 else int(numbers[0]))
        return (0, 0)
    
    for section in sections:
        if section.strip():

            lines = section.strip().split('\r\n\r\n')## changed here
            # print(len(lines) if len(lines) > 1 else "no notes")
            # print(lines)
            # print(len(lines))
            if len(lines) > 1:
                # print(2)
                title_location = lines[0].strip().split('\n') 
                book_notes = lines[1]
                # print(type(book_notes))

                book_title = title_location[0]
                note_location = title_location[1]

   
                if book_title not in books:
                    books[book_title] = []

                current_loc = get_location_numbers(note_location.split('|')[-2])
                note_key = (book_title, current_loc[0])  # Use start location in key

                # Check if the last note has the same start location
                should_add = True
                if len(books[book_title]) > 0:
                    last_note_loc_text = books[book_title][-1][1]
                    last_note_loc = get_location_numbers(last_note_loc_text.split('|')[-2])
                    if last_note_loc[0] == current_loc[0]:
                        should_add = False
                        if last_note_loc[1] < current_loc[1]:
                            #directly replace the last note with the current note
                            books[book_title][-1] = (book_notes, note_location)

                # break
                if should_add and note_key not in seen:
                    seen.add(note_key)
                    books[book_title].append((book_notes, note_location))  
                    # print(note_location.split('|')[-2])
                    # print(re.search(pattern, note_location.split('|')[-2]).group(1))
    return books

@app.post("/process-notes")
async def process_file(kindle_content: KindleContent):
    # print(kindle_content.content)
    try:
        processed_data = process_kindle_notes(kindle_content.content)
        # print(processed_data)
        return processed_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
