Here’s a quick rundown of the changes I made:

1. Added three new avatar styles—lorelei (🎨, 500 pts), bottts (🤖, 500 pts), and adventurer (⚔, 750 pts)—to the shop with type avatar_style so they fit the existing themes logic.  
2. Adjusted mystery box rewards: the small box can drop lorelei or bottts (not adventurer), while the large box can drop all three styles along with points, themes, and premium items.  
3. When users get an avatar style, it’s recorded with type 'avatar_style' and cost 0 to track ownership properly.  
4. Modified purchase restrictions to prevent buying the same avatar style twice by including avatar_style in the non-consumables check.  
5. Integrated with existing system routes and UI so purchased avatar styles show up and can be selected only if owned.  
6. Kept all previous badge, points, and purchase logic untouched to maintain smooth backward compatibility.

Here’s a simple breakdown of the changes in auth/routes.py and related templates:
1. AvatarForm now uses single-selection SelectField for hair and background color (matching DiceBear’s API), but wraps them in lists when saving for schema consistency.

2. The /settings route:  
   - Dynamically fills avatar choices using themes helpers.  
   - Separately handles avatar form submissions alongside general settings and password changes.  
   - Validates avatar options before updating user preferences.  
   - Preloads forms with user data, defaulting avatar to avataaars if none set.

3. Added /change_password route to handle password updates per settings.html form action.

4. In settings.html:  
   - Inserted a new avatar customization form with style, hair, background color, flip options, plus a live avatar preview image.  
   - Uses Bootstrap styling and shows errors nicely.

5. Avatar preview uses JavaScript to fetch an SVG preview from /themes/api/avatar_preview/<style> when style changes or page loads.

6. In profile.html replaced icon with an avatar image built from DiceBear URL, using user avatar preferences and username as seed, ensuring consistent size and style.

7. Notes:  
   - Preview only updates by avatar style now; extending preview to include hair, color, flip needs API enhancement.  
   - The change to single selection simplifies UI as DiceBear expects single values per option.

All existing forms, layouts, and flash messages remain as before for a smooth UX.
