# Installing Webfonts
Follow these simple Steps.

## 1.
Put `gambetta/` Folder into a Folder called `fonts/`.

## 2.
Put `gambetta.css` into your `css/` Folder.

## 3. (Optional)
You may adapt the `url('path')` in `gambetta.css` depends on your Website Filesystem.

## 4.
Import `gambetta.css` at the top of you main Stylesheet.

```
@import url('gambetta.css');
```

## 5.
You are now ready to use the following Rules in your CSS to specify each Font Style:
```
font-family: Gambetta-Light;
font-family: Gambetta-LightItalic;
font-family: Gambetta-Regular;
font-family: Gambetta-Italic;
font-family: Gambetta-Medium;
font-family: Gambetta-MediumItalic;
font-family: Gambetta-Semibold;
font-family: Gambetta-SemiboldItalic;
font-family: Gambetta-Bold;
font-family: Gambetta-BoldItalic;
font-family: Gambetta-Variable;
font-family: Gambetta-VariableItalic;

```
## 6. (Optional)
Use `font-variation-settings` rule to controll axes of variable fonts:
wght 300.0wght 700.0

Available axes:
'wght' (range from 300.0 to 700.0'wght' (range from 300.0 to 700.0

