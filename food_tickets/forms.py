from django import forms


class UploadExcelForm(forms.Form):
    file = forms.FileField(label="Файл excel с данными по питанию")

