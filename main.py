# kindle_api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","https://zindex-zyn.vercel.app"],  # Your React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define data models 
class KindleContent(BaseModel):
    content: str

# class BookNote(BaseModel):
#     title: str
#     notes: List[str]

def process_kindle_notes(content: str) -> dict:
    books = {}
    sections = content.split('==========')
    seen = set()
    # print(sections)
    
    for section in sections:
        if section.strip():

            lines = section.strip().split('\r\n\r\n')
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


                note_key = (book_title, book_notes)
                if note_key not in seen:
                    seen.add(note_key)
                    books[book_title].append((book_notes, note_location))  
    # print(books)
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
