# pdf_manager
A python PDF manager that does it all.

# Examples

```python
from pdf_manager import PDF_Manager


PDF_Manager().add("doc1.pdf").add("doc2.pdf").save("merged.pdf")

PDF_Manager("long_document.pdf").split().keep([0, 1]).save("first_two_pages.pdf")

PDF_Manager("upside_down.pdf").rotate(180).save("upside_up.pdf")

PDF_Manager().add_from_images([f"img_{i}.png" for i in range(3)]).save("high_quality.pdf").shrink().save("low_quality.pdf")

PDF_Manager("my_account.pdf").hide_content(r"password[\t\sa-zA-Z0-9]+").save("my_account_hidden.pdf")
```
