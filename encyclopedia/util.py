import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir("entries")
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"entries/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content.encode('ascii') ))


def get_entry(title):
    """
    Retrieves an encyclopedia entry by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"entries/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None


def to_html(text): #I have to find a way to make things work on different lines (at least bold and list)
    line_split = text.splitlines()
    markdown_dict = {}
    h6 = re.compile("#{6,6}")
    h5 = re.compile("#{5,5}")
    h4 = re.compile("#{4,4}")
    h3 = re.compile("#{3,3}")
    h2 = re.compile("#{2,2}")
    h1 = re.compile("#{1,1}")
    lists_a = re.compile("\*")
    lists_b = re.compile("-")
    bold = re.compile("(\*\*.+?\*\*)")
    link = re.compile("(\[.+?\]\(.+?\))")
    
    i = 0 
    def header(size, text, name, iterator):
        if size.match(text):
            text = size.sub('', text)
            markdown_dict[text] = str(name)
            iterator += 1
        return iterator
            
    length = len(line_split)
    
    while i < length:  
    
        if line_split[i] == "":
            if line_split[i+1] and line_split[i-1] and (i+1) < length and (i-1) >= 0:
                markdown_dict[line_split[i]] = 'close_open_p'
                i += 1
            elif line_split[i+1] and (i+1) < length:
                markdown_dict[line_split[i]] = 'open_p'
                i += 1
            elif line_split[i-1] and (i-1) >= 0:
                markdown_dict[line_split[i]] = 'close_p'  
                i += 1
    
        if h6.match(line_split[i]):
            i = header(h6, line_split[i], 'h6', i)
        elif h5.match(line_split[i]):
            i = header(h5, line_split[i], 'h5', i)
        elif h4.match(line_split[i]):
            i = header(h4, line_split[i], 'h4', i)
        elif h3.match(line_split[i]):
            i = header(h3, line_split[i], 'h3', i)
        elif h2.match(line_split[i]):
            i = header(h2, line_split[i], 'h2', i)
        elif h1.match(line_split[i]):
            i = header(h1, line_split[i], 'h1', i)
        
        if i >= length:  
            break
        
      
        
        if bold.search(line_split[i]) or link.search(line_split[i]):
            line_split_bold_link = re.split("(\*\*.+?\*\*|\[.+?\]\(.+?\))", line_split[i])# split line by bold and link sections including them
            bold_link_dict = {}   # create empty dictionary
            for value in line_split_bold_link: # iterate over each string and find out whether it needs to be bolded or not
                value = str(value)
                if bold.match(value):
                    value = value[2:] #delete first **
                    end_value_to_delete = len(value) - 2 
                    value = value[:end_value_to_delete] # delete last **
                    bold_link_dict[value] = 'bold' #populate the dictionary
                elif link.match(value): # elif for now, maybe try if so you can do both at same time?
                    link_splitter = re.compile("\]\(")
                    link_split_list = link_splitter.split(value)
                    text = link_split_list[0][1:]
                    url = link_split_list[1]
                    end_value_to_delete = len(url) - 1
                    url = url[:end_value_to_delete] # deletes last ]
                    url_splitter = re.compile('/')
                    url = url_splitter.split(url)[-1] # gets only the last link part like 'python' or 'html'
                    split_link_tuple = (text, url)
                    bold_link_dict[split_link_tuple] = 'link' #populate the dictionary
                else:
                    bold_link_dict[value] = 'normal' # populate the dictionary
            
            bold_link_tuple = tuple([(k, v) for k, v in bold_link_dict.items()]) # create a list of tuples of the dictionary objects, then turn the list into a tuple
            markdown_dict[bold_link_tuple] = 'bold_and_link' # add tuple to final dictionary
            i += 1
   
        # lists
        elif lists_a.match(line_split[i]) or lists_b.match(line_split[i]): #checks for the beggining list item
            line_split[i] = line_split[i][1:] # deletes the star at the beginning
            lists_list = [line_split[i]] # adds first list item to new list list
            i += 1
            if i < length:
                while lists_a.match(line_split[i]) or lists_b.match(line_split[i]) or line_split[i] == "": # checks for each new list item until the list is over
                    if line_split[i] == "":
                        i += 1  
                        continue
                    line_split[i] = line_split[i][1:] # deletes the star at the beginning
                    lists_list.append(line_split[i]) # adds each new list item to list list
                    i += 1
                    if i >= length: #break condition just in case
                        break
            lists_list = tuple(lists_list) # converts to tuple
            markdown_dict[lists_list] = 'list'   # adds final tuple containing all bullet points to markdown_dict
                #continue - i am not sure if I need this or not
        
        else:
            if line_split[i]:
                markdown_dict[line_split[i]] = 'other'
                i += 1 
            else:
                if line_split[i+1] and line_split[i-1] and (i+1) < length and (i-1) >= 0:
                    markdown_dict[line_split[i]] = 'close_open_p'
                    i += 1
                elif line_split[i+1] and (i+1) < length:
                    markdown_dict[line_split[i]] = 'open_p'
                    i += 1
                elif line_split[i-1] and (i-1) >= 0:
                    markdown_dict[line_split[i]] = 'close_p'  
                    i += 1
            
    
    return markdown_dict  

"""
I am going to keep this function just in case, delete it before turning in:


def search_like(search_query, item_to_be_compared_to):
    i = 0
    counter_list = []
    smaller_string = min(len(search_query), len(item_to_be_compared_to))
    while i < smaller_string:
        if search_query[i] == item_to_be_compared_to[i]:
            counter_list.append(1)
        i += 1
    if len(counter_list) == smaller_string:
        return True
    else:
        return False
"""