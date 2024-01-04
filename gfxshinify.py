from git import Repo
import git, os, glob, re, time
from google.oauth2 import service_account
from googleapiclient.discovery import build

folder = r"C:\mod\git-days-of-europe"
service_account_key_file = r'C:\stable-store-399704-c6ba6f5a1c17.json'


def switchbranch(branch):
    repo = Repo(folder)
    assert not repo.bare
    repo.git.checkout(branch)
    repo.git.pull('origin', branch)

def pushtobranch(branch):
    repo = Repo(folder)
    assert not repo.bare
    repo.git.add('.')
    repo.index.commit('loc')
    repo.git.push('origin',branch)

def shinify(namespace):
    captured_icons = set()  # Use a set to store unique values
    for file in glob.glob(os.path.join(folder, fr'common\national_focus\TNO_{namespace}*.txt')):
        filename = os.path.basename(file)
        with open(file, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, start=1):
                # Check if the line starts with "#" or matches variations of "icon =" in a case-insensitive way
                match = re.search(r'\bicon\s*=\s*(\S+)', line, flags=re.IGNORECASE)
                if match and not line.lstrip().startswith('#'):
                    captured_icons.add(match.group(1))

    print(len(list(captured_icons)))

def read_paragraph_element(element):
   
    text_run = element.get('textRun')
    if not text_run:
        return ''
    return text_run.get('content')


def read_structural_elements(elements):
    
    text = ''
    for value in elements:
        if 'paragraph' in value:
            elements = value.get('paragraph').get('elements')
            for elem in elements:
                text += read_paragraph_element(elem)
        elif 'table' in value:
            # The text in table cells are in nested Structural Elements and tables may be
            # nested.
            table = value.get('table')
            for row in table.get('tableRows'):
                cells = row.get('tableCells')
                for cell in cells:
                    text += read_structural_elements(cell.get('content'))
        elif 'tableOfContents' in value:
            # The text in the TOC is also in a Structural Element.
            toc = value.get('tableOfContents')
            text += read_structural_elements(toc.get('content'))
    return text

def submitloc(google_docs_link):

    match = re.search(r'/document/d/([a-zA-Z0-9_-]+)', google_docs_link)
    if not match:
        raise ValueError("Invalid Google Docs link")

    # Extract the document ID from the match
    document_id = match.group(1)

    # Authenticate with the service account key file
    credentials = service_account.Credentials.from_service_account_file(
        service_account_key_file,
        scopes=['https://www.googleapis.com/auth/documents.readonly']
    )

    # Create a Google Docs API service object
    service = build('docs', 'v1', credentials=credentials)

    # Use the Google Docs API to get the document content
    document = service.documents().get(documentId=document_id).execute()

    elements = document.get('body').get('content')
    
    elements = (read_structural_elements(elements))
    pattern = r"((?:Event|Focus):.*?)(\n|$)"
    matches = re.findall(pattern, elements, re.DOTALL)
    
    event_lines = [match[0].strip() for match in matches]
    
    
    pattern = r'Title:(.*?)(\n|$)'
    matches = re.findall(pattern, elements, re.DOTALL)
    extracted_text_after_title = [match[0].strip() for match in matches]
    pattern = r'Text:(.*?)(Button:|$)'
    matches = re.findall(pattern, elements, re.DOTALL)

    extracted_text_sections = [match[0].strip() for match in matches]
    pattern = r'Button:(.*?)(\n|$)'
    matches = re.findall(pattern, elements, re.DOTALL)
    extracted_text_after_button = [match[0].strip() for match in matches]

    sections_list = []

    for i in range(len(event_lines)):
        cleaned_text_section = re.sub(r'\n','', extracted_text_sections[i])
        loctype = 0
        if "Event" in event_lines[i].strip():
            loctype = 0
            event_lines[i]= event_lines[i].replace("Event: ",'',1)
        elif "Focus" in event_lines[i].strip():
            loctype=1
            event_lines[i]= event_lines[i].replace("Focus: ",'',1)
        section_dict = {
            "codev": event_lines[i].strip().replace(" ","_"),
            "title": extracted_text_after_title[i].strip(),
            "text":  cleaned_text_section.strip(),
            "button": extracted_text_after_button[i].strip(),
            "type": loctype
        }
        sections_list.append(section_dict)

    return sections_list

def implementloc(namespace,list):
    
    with open(os.path.join(folder,fr"localisation\english\TNO_{namespace}_l_english.yml"),"r",encoding="utf-8") as file:
        yml_content = file.read()
    yml_content=yml_content+'\n'
    holder=''
    for doc in list:
        for section in doc:
            if (section['type']==0):
                holder+=f' {section["codev"]}.t:0 "{section["title"]}"\n {section["codev"]}.desc:0 "{section["text"]}"\n {section["codev"]}.a:0 "{section["button"]}"\n\n'
            
    
    updated_yml = yml_content+holder
    with open(os.path.join(folder,fr"localisation\english\TNO_{namespace}_l_english.yml"), "w", encoding="utf-8") as file:
        file.write(updated_yml)

