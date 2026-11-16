// Independent language switcher: works even when other interactive features fail.
(()=>{'use strict';
const btn=document.getElementById('languageBtn');if(!btn)return;
const entries=[
['.hero .eyebrow','A MOVEMENT FOR SAFER ROADS','सुरक्षित सड़कों के लिए एक अभियान'],
['.hero h1','Every journey<br>deserves a <em>safe</em><br>arrival.','हर सफ़र का<br><em>सुरक्षित</em> अंत<br>होना चाहिए।',true],
['.hero p',"Road safety isn't just about roads. It's about people, families and the futures we protect. Together, we can make every journey safer.",'सड़क सुरक्षा केवल सड़कों की बात नहीं है। यह लोगों, परिवारों और उनके भविष्य की सुरक्षा है। मिलकर हर यात्रा को सुरक्षित बनाएं।'],
['.heroactions a:first-child','Explore Our Work','हमारा काम देखें'],
['.heroactions a:last-child','Join the Movement','अभियान से जुड़ें'],
['#library h2','Road safety <span>toolkit.</span>','सड़क सुरक्षा <span>संसाधन।</span>',true],
['#faq h2','Questions about<br><span>road safety.</span>','सड़क सुरक्षा से जुड़े<br><span>सवाल।</span>',true],
['#quiz h2','How road-safe <span>are you?</span>','आप सड़क सुरक्षा के बारे में <span>कितना जानते हैं?</span>',true],
['#quiz .container > p','Test your knowledge with a quick five-question quiz.','पाँच सवालों से अपना ज्ञान परखें।'],
['#report h2',null,'सड़क पर कोई ख़तरा देखा?'],
['#campaigns h2',null,'सड़क सुरक्षा अभियान से जुड़ें।'],
['nav a[href="#quiz"]','Quiz','क्विज़'],['nav a[href="#report"]','Report a Hazard','ख़तरा रिपोर्ट करें'],['nav a[href="#campaigns"]','Campaigns','अभियान'],['nav a[href="#about"]','About Us','हमारे बारे में'],['nav a[href="#focus"]','Our Work','हमारा काम'],['nav a[href="#impact"]','Our Impact','हमारा प्रभाव'],['nav a[href="#resources"]','Resources','संसाधन'],['nav a[href="#guides"]','Safety Guides','सुरक्षा सुझाव'],['nav a[href="#contact"]','Contact','संपर्क'],
['#library .resource-downloads a:nth-child(1)',null,'सुरक्षा चेकलिस्ट डाउनलोड करें'],['#library .resource-downloads a:nth-child(2)',null,'दुर्घटना सहायता गाइड डाउनलोड करें'],
];
const nodes=entries.map(([selector,en,hi,markup])=>{const el=document.querySelector(selector);return el?{el,en:en??(markup?el.innerHTML:el.textContent),hi,markup:!!markup}:null}).filter(Boolean);
let current='en';btn.addEventListener('click',()=>{current=current==='en'?'hi':'en';for(const n of nodes){const val=current==='hi'?n.hi:n.en;if(n.markup)n.el.innerHTML=val;else n.el.textContent=val;}document.documentElement.lang=current;btn.textContent=current==='hi'?'English':'हिन्दी';btn.setAttribute('aria-label',current==='hi'?'Switch to English':'हिन्दी में देखें');});
})();
