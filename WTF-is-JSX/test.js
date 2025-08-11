const ITEMS = 'hello there people'.split(' ');

// turn an Array into list items: 
let list = items => items.map( p => <li> {p} </li> );
 
// view with a call out ("partial") to generate a list from an Array:
let vdom = (
    <div id="foo">
        <p>Look, a simple JSX DOM renderer!</p>
        <ul>{ list(ITEMS) }</ul>
    </div>
);
 
// render() converts our "virtual DOM" (see below) to a real DOM tree:
let dom = render(vdom);
 
// append the new nodes somewhere:
document.body.appendChild(dom);
 
// Remember that "virtual DOM"? It's just JSON - each "VNode" is an object with 3 properties.
let json = JSON.stringify(vdom, null, '  ');

// The whole process (JSX -> VDOM -> DOM) in one step:
document.body.appendChild(
    render( <pre id="vdom">{ json }</pre> )
);