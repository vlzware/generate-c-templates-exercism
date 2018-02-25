# generate_c_template.py
Python script generating a template for implementing C exercises for http://exercism.io

Here is the list with the unimplemented C exercises:
http://exercism.io/languages/c/todo

Call the script with the name (slug) of a exercise as parameter like this:
```
./generate_c_template.py prime-factors
```

On success it generates the expected directories, copies 'vendor', creates and populates all expected files.
