import wikipedia

def get_object_details(detected_classes):
    details = []
    seen_classes = set()  # To keep track of processed class names

    for cls in detected_classes:
        cls_lower = cls.lower()  # Normalize for duplicates
        if cls_lower in seen_classes:
            continue  # Skip if already processed
        seen_classes.add(cls_lower)

        try:
            summary = wikipedia.summary(cls, sentences=5)
            details.append({
                "name": cls.title(),
                "description": summary,
                "usage": "Usage information not available.",
                "benefits": "Benefits information not available.",
                "origin": "Origin information not available.",
                "summary": summary,
                "question": f"Would you like to know more about this {cls}?"
            })
        except wikipedia.exceptions.DisambiguationError as e:
            details.append({
                "name": cls.title(),
                "description": f"Multiple entries found: {e.options}",
                "usage": "",
                "benefits": "",
                "origin": "",
                "summary": "",
                "question": f"Would you like to know more about this {cls}?"
            })
        except wikipedia.exceptions.HTTPTimeoutError:
            details.append({
                "name": cls.title(),
                "description": "Wikipedia request timed out.",
                "usage": "",
                "benefits": "",
                "origin": "",
                "summary": "",
                "question": f"Would you like to know more about this {cls}?"
            })
        except Exception as e:
            details.append({
                "name": cls.title(),
                "description": f"Error fetching data: {str(e)}",
                "usage": "",
                "benefits": "",
                "origin": "",
                "summary": "",
                "question": f"Would you like to know more about this {cls}?"
            })

    return details

def get_cross_question(cls_name: str):
    return f"Would you like to know more about this {cls_name}?"
