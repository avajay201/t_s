import re



def serializer_first_error(serializer):
    '''
    Extracts and formats the first validation error message from a given serializer.
    '''
    try:
        error_key = list(serializer.errors.keys())[0]
        error_value = list(serializer.errors.values())[0][0]
        error_value = error_value.replace('This field', error_key).replace('_', ' ')
        cleaned_error = re.sub(r'[^a-zA-Z0-9 ]', '', error_value)
        return cleaned_error.capitalize()
    except Exception as err:
        print('Error:', err)
        return 'Something went wrong.'
