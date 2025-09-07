Here’s a quick rundown of the changes I made:

1. Added three new avatar styles—lorelei (🎨, 500 pts), bottts (🤖, 500 pts), and adventurer (⚔, 750 pts)—to the shop with type avatar_style so they fit the existing themes logic.  
2. Adjusted mystery box rewards: the small box can drop lorelei or bottts (not adventurer), while the large box can drop all three styles along with points, themes, and premium items.  
3. When users get an avatar style, it’s recorded with type 'avatar_style' and cost 0 to track ownership properly.  
4. Modified purchase restrictions to prevent buying the same avatar style twice by including avatar_style in the non-consumables check.  
5. Integrated with existing system routes and UI so purchased avatar styles show up and can be selected only if owned.  
6. Kept all previous badge, points, and purchase logic untouched to maintain smooth backward compatibility.
