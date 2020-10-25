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


def to_html(text):

    # create necessary regex objects
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
   
    # split text into individual lines
    line_split = text.splitlines()

    # define a function to deal with headers (h1 - h6)
    def header(size, text, name):
        new_list = []
        for line in text: 
            if size.match(line):  # if the line starts with the specific size (# - ######)
                line = size.sub(f'<{str(name)}>', line)  # replace the hashtags with the appropriate header tag
                line += f'</{str(name)}>'  # add the closing header tag onto the line
            new_list.append(line)  # add each line, whether it has been altered or not, to a new list that eventually is returned
        return new_list
        
    # define function to deal with bold and links in markdown, similar to the one above
    def bold_or_link(attribute, text, name):
        new_line_list = []
        for line in text:
            if attribute.search(line):  # if there is a bold or link markdown syntax in the line
                attribute_split_list = attribute.split(line)  # split the line by the attribute in question
                new_attribute_list = []
                for value in attribute_split_list:  # loop over each value in the attribute split list
                    if attribute.match(value):  # if the attribute starts with the appropriate markdown syntax
                        if name == "bold":  # for bold
                            value = value[2:(len(value) - 2)]  # deletes the ** at the beginning and end
                            value = f"<b>{value}</b>"  # adds bold html tags
                        elif name == "link":  # for links
                            link_split_list = re.split("\]\(", value)  # splits the link into the text part and url part
                            text = link_split_list[0][1:]  # deletes the first [
                            url = link_split_list[1]
                            url = url[:(len(url) - 1)]  # deletes the last )
                            value = f'<a href="{url}">{text}</a>'  # adds the url and text together in an html <a> tag
                    new_attribute_list.append(value)  # adds the value to a new list, no matter if it has been modified or not
                line = "".join(new_attribute_list)  # joins the list back into a string
            new_line_list.append(line)  # adds the line to a new list, no matter if it has been modified or not
        return new_line_list
        
    # each of these runs the appropriate function to deal with its attribute and returns the modified line_split
    line_split = header(size=h6, text=line_split, name="h6")
    line_split = header(size=h5, text=line_split, name="h5")
    line_split = header(size=h4, text=line_split, name="h4")
    line_split = header(size=h3, text=line_split, name="h3")
    line_split = header(size=h2, text=line_split, name="h2")
    line_split = header(size=h1, text=line_split, name="h1")
    line_split = bold_or_link(attribute=bold, text=line_split, name="bold")
    line_split = bold_or_link(attribute=link, text=line_split, name="link")
    
    # for html lists
    i = 0
    list_list = []
    while i < len(line_split):  # loops through entire line_split
        if lists_a.match(line_split[i]) or lists_b.match(line_split[i]): #checks for the beggining list item
            list_list.append("<ul>")  # adds opening <ul> tag
            line_split[i] = line_split[i][1:] # deletes the star at the beginning
            list_list.append(f"<li>{line_split[i]}</li>")  # adds first list item
            i += 1
            if i < len(line_split):
                while lists_a.match(line_split[i]) or lists_b.match(line_split[i]): # checks for each new list item until the list is over
                    line_split[i] = line_split[i][1:] # deletes the star at the beginning
                    list_list.append(f"<li>{line_split[i]}</li>")# adds each new list item to list list
                    i += 1
                    if i >= len(line_split): #break condition just in case
                        break
            list_list.append("</ul>") # adds closing </ul> tag once list is over
        else:  # if the line is not part of markdown list, 
            list_list.append(f"{line_split[i]}\n")  # adds a newline character (\n) at the end of every line so it looks better when converted to HTML
            i += 1
    line_split = list_list
    
    return line_split
    