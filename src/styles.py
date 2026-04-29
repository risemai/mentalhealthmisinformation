"""
styles.py — Global CSS definitions for Veritas Analytics App.
"""


def get_global_css() -> str:
    return """
<style>
/* 
   FONTS
 */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Mono:wght@400;500&family=Playfair+Display:wght@700;800&display=swap');

/* 
   ROOT VARIABLES
 */
:root {
    --bg-main:      #F8F9FA;
    --bg-white:     #FFFFFF;
    --bg-soft:      #F0F2F5;
    --text-dark:    #212529;
    --text-mid:     #495057;
    --text-light:   #868E96;
    --border:       #DEE2E6;
    --shadow-sm:    0 2px 8px rgba(0,0,0,0.06);
    --shadow-md:    0 4px 20px rgba(0,0,0,0.08);
    --shadow-lg:    0 8px 40px rgba(0,0,0,0.12);
    --radius-sm:    8px;
    --radius-md:    15px;
    --radius-lg:    24px;
    /* accent palette */
    --emerald:      #10B981;
    --emerald-light:#D1FAE5;
    --amber:        #F59E0B;
    --amber-light:  #FEF3C7;
    --indigo:       #6366F1;
