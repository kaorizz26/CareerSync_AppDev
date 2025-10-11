# import re
# import json

# def parse_ai_output(raw_output):
#     """
#     Extract JSON object from AI output string.
#     Works whether or not it is inside ```json``` code blocks.
#     """
#     # Remove <think> tags
#     raw_output = re.sub(r'<\/?think>', '', raw_output, flags=re.IGNORECASE)

#     # Regex to match JSON object
#     match = re.search(r'(\{(?:.|\s)*\})', raw_output)
#     if match:
#         json_str = match.group(1)

#         # Remove comments (// or /* */)
#         json_str = re.sub(r'//.*?\n', '', json_str)
#         json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)

#         try:
#             return json.loads(json_str)
#         except json.JSONDecodeError:
#             return {"error": "Invalid JSON inside AI output after cleaning", "raw_output": raw_output}
#     else:
#         return {"error": "No JSON found in AI output", "raw_output": raw_output}
