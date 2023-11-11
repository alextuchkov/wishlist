// document.addEventListener('DOMContentLoaded', function() {
//     document.querySelectorAll('.book-button, .split-button').forEach(function(button) {
//         button.addEventListener('click', async function() {
//             try {
//                 var item_id = this.getAttribute('data-item-id');
//                 var ref_id = this.getAttribute('data-ref-id');

//                 // if button clicked is book, then do:
//                 const postResponse = await fetch("/book", {
//                     method: 'POST',
//                     headers: {
//                         'Content-Type': 'application/json',
//                         'X-CSRFToken': csrfToken
//                     },
//                     body: JSON.stringify({
//                         'item-id': item_id,
//                         'ref-id': ref_id
//                     })
//                 });

//                 // if button clicked is split, then do:
//                 // new code goes here:

//                 // and then do the code below

//                 if (!postResponse.ok) {
//                     throw new Error('Network response was not ok');
//                 }

//                 const postData = await postResponse.json();
//                 console.log('POST Request Successful:', postData);

//                 // Now, redirect to the new page using the standard form of navigation
//                 window.location.href = `/list/${ref_id}`;

//             } catch (error) {
//                 console.error('There was a problem with the fetch operation:', error);
//             }
//         });
//     });
// });

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.book-button, .split-button').forEach(function(button) {
        button.addEventListener('click', async function() {
            try {
                var item_id = this.getAttribute('data-item-id');
                var ref_id = this.getAttribute('data-ref-id');

                if (this.classList.contains('book-button')) {
                    const postResponse = await fetch("/book", {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({
                            'item-id': item_id,
                            'ref-id': ref_id
                        })
                    });

                    if (!postResponse.ok) {
                        throw new Error('Network response was not ok');
                    }

                    const postData = await postResponse.json();
                    console.log('POST Request Successful:', postData);

                    window.location.href = `/list/${ref_id}`;    
                } 
                
                // Split
                else if (this.classList.contains('split-button')) {
     
                    const splitResponse = await fetch("/split", {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({
                            'item-id': item_id,
                            'ref-id': ref_id
                        })
                    });

                    if (!splitResponse.ok) {
                        throw new Error('Network response was not ok');
                    }

                    const splitData = await splitResponse.json();
                    console.log('SPLIT Request Successful:', splitData);

                    window.location.href = `/list/${ref_id}`;
                }

            } catch (error) {
                console.error('There was a problem with the fetch operation:', error);
            }
        });
    });
});

