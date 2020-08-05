# OXMLpy
Embed XXE payload into Open XML file formats

Will generate a singular OXML document for each XML contained in the sample (input) OXML document.
Made originally for xlsx document.

## Todo
1 - Expand to generate a larger variety of payloads to choose

2 - Add compatibility to other OXML files (pptx, docx, ...)

3 - Include XSS payloads

## Example usage

```bash
./oxmlpy.py -f data.xlsx -i 10.10.10.10 -o out_dir
```
