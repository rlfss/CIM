new Mmenu(document.querySelector('#menu'),
    {
        drag: false,
        pageScroll: {
            scroll: true,
            update: true
        },
        sidebar: {
            expanded: {
                use: '(min-width: 1300px)',
            }
        },
        navbars: [
            {
                content: ['<div><a class="d-block" href="index.html"><img src="./images/logo.png"></a></div>', 'close']
            }
        ]
    }
);

//Date Range

