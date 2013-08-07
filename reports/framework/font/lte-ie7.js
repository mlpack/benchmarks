/* Load this script using conditional IE comments if you need to support IE 7 and IE 6. */

window.onload = function() {
	function addIcon(el, entity) {
		var html = el.innerHTML;
		el.innerHTML = '<span style="font-family: \'icomoon\'">' + entity + '</span>' + html;
	}
	var icons = {
			'icon-stats' : '&#xe000;',
			'icon-bars' : '&#xe001;',
			'icon-bars-2' : '&#xe002;',
			'icon-pie' : '&#xe003;',
			'icon-info' : '&#xe004;',
			'icon-info-2' : '&#xe005;',
			'icon-question' : '&#xe006;',
			'icon-html5' : '&#xe007;',
			'icon-css3' : '&#xe008;',
			'icon-html5-2' : '&#xe009;',
			'icon-paragraph-right' : '&#xe00a;',
			'icon-paragraph-justify' : '&#xe00b;',
			'icon-paragraph-left' : '&#xe00c;',
			'icon-paragraph-center' : '&#xe00d;',
			'icon-paragraph-right-2' : '&#xe00e;',
			'icon-paragraph-justify-2' : '&#xe00f;',
			'icon-indent-increase' : '&#xe010;',
			'icon-indent-decrease' : '&#xe011;',
			'icon-share' : '&#xe012;',
			'icon-libreoffice' : '&#xe013;',
			'icon-file-pdf' : '&#xe014;',
			'icon-file-openoffice' : '&#xe015;',
			'icon-file-word' : '&#xe016;',
			'icon-file-excel' : '&#xe017;',
			'icon-file-zip' : '&#xe018;',
			'icon-file-powerpoint' : '&#xe019;',
			'icon-file-xml' : '&#xe01a;',
			'icon-file-css' : '&#xe01b;'
		},
		els = document.getElementsByTagName('*'),
		i, attr, html, c, el;
	for (i = 0; ; i += 1) {
		el = els[i];
		if(!el) {
			break;
		}
		attr = el.getAttribute('data-icon');
		if (attr) {
			addIcon(el, attr);
		}
		c = el.className;
		c = c.match(/icon-[^\s'"]+/);
		if (c && icons[c[0]]) {
			addIcon(el, icons[c[0]]);
		}
	}
};