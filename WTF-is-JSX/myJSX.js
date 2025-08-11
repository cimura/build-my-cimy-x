/** @jsx h */
//let var = <div id="foo">Hello!</div>;
//let var = h('div', {id:"foo"}, 'Hello');

function h(nodeName, attributes, ...args) {
	let children = args.length ? [].concat(...args) : null;
	return { nodeName, attributes, children};
}

function render(vnode) {
	// vnodeをtextノードに変更
	if (vnode.split) vnode.createTextNode(vnode)

	// vnodeのノード名を使用してDOM要素を作成
	let n = document.createElement(vnode.nodeName);

	// attributeを新しいノードに挿入
	let a = vnode.attributes || {};
	Object.keys(a).forEach( k => n.setAttribute(k, a[k]) );

	// renderして子ノードにアペンドする
	(vnode.children || []).forEach( c => n.appendChild(render(c)) )
}

// Array of strings we want to show in a list:
let items = ['foo', 'bar', 'baz'];

// creates one list item given some text:
function item(text) {
    //return <li>{text}</li>;
    return h("li", null, text);
}

// a "view" with "iteration" and "a partial":
let list = render(
//  <ul>
//    { items.map(item) }
//  </ul>
    h ("ul", null, items.map(item))
);

document.body.appendChild(list)