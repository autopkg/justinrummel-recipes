TeamViewer QS and Full app pkg and JSS
===

This is based off of https://github.com/autopkg/hjuutilainen-recipes/tree/master/TeamViewer QS and Full download recipes.  Be sure that his is part of your AutoPKG by running:

``` bash
autopkg repo-add https://github.com/autopkg/hjuutilainen-recipes
```

Note that the TeamViewer recipe contains a preinstall script which prevents the application opening during installation. This is necessary to prevent PPPC warnings mid-installation. 

If overriding the recipe, you need to ensure that the preinstall script, ScriptTemplate file, and icon are in your RecipeOverrides directory.