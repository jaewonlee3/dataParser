import json

def myParser(inputDto):
    outputDto = inputDto['dto']
    outputDto['add_key'] = 'my_value'
    return outputDto