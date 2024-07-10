# Installing Webfonts
Follow these simple Steps.

## 1.
Put `epilogue/` Folder into a Folder called `fonts/`.

## 2.
Put `epilogue.css` into your `css/` Folder.

## 3. (Optional)
You may adapt the `url('path')` in `epilogue.css` depends on your Website Filesystem.

## 4.
Import `epilogue.css` at the top of you main Stylesheet.

```
@import url('epilogue.css');
```

## 5.
You are now ready to use the following Rules in your CSS to specify each Font Style:
```
font-family: Epilogue-Thin;
font-family: Epilogue-ThinItalic;
font-family: Epilogue-ExtraLight;
font-family: Epilogue-ExtraLightItalic;
font-family: Epilogue-Light;
font-family: Epilogue-LightItalic;
font-family: Epilogue-Regular;
font-family: Epilogue-Italic;
font-family: Epilogue-Medium;
font-family: Epilogue-MediumItalic;
font-family: Epilogue-SemiBold;
font-family: Epilogue-SemiBoldItalic;
font-family: Epilogue-Bold;
font-family: Epilogue-BoldItalic;
font-family: Epilogue-ExtraBold;
font-family: Epilogue-ExtraBoldItalic;
font-family: Epilogue-Black;
font-family: Epilogue-BlackItalic;
font-family: Epilogue-Variable;
font-family: Epilogue-VariableItalic;

```
## 6. (Optional)
Use `font-variation-settings` rule to controll axes of variable fonts:
wght 400.0

Available axes:
'wght' (range from 100.0 to 900.0

