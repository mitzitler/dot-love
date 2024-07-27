# Installing Webfonts
Follow these simple Steps.

## 1.
Put `bespoke-stencil/` Folder into a Folder called `fonts/`.

## 2.
Put `bespoke-stencil.css` into your `css/` Folder.

## 3. (Optional)
You may adapt the `url('path')` in `bespoke-stencil.css` depends on your Website Filesystem.

## 4.
Import `bespoke-stencil.css` at the top of you main Stylesheet.

```
@import url('bespoke-stencil.css');
```

## 5.
You are now ready to use the following Rules in your CSS to specify each Font Style:
```
font-family: BespokeStencil-Light;
font-family: BespokeStencil-LightItalic;
font-family: BespokeStencil-Regular;
font-family: BespokeStencil-Italic;
font-family: BespokeStencil-Medium;
font-family: BespokeStencil-MediumItalic;
font-family: BespokeStencil-Bold;
font-family: BespokeStencil-BoldItalic;
font-family: BespokeStencil-Extrabold;
font-family: BespokeStencil-ExtraboldItalic;
font-family: BespokeStencil-Variable;
font-family: BespokeStencil-VariableItalic;

```
## 6. (Optional)
Use `font-variation-settings` rule to controll axes of variable fonts:
wght 800.0

Available axes:
'wght' (range from 300.0 to 800.0

