function query_suggest(keywords){
        suggestion_dom = document.getElementById('suggestion');
        $.ajax({
            type : "get",
            async: true,
            url : "/suggest?keywords="+keywords,
            success : function(data){
                console.log(data)
                var tag = '';
                for(var i=0;i<data.length;i++){
                    tag += '<li>'+data[i]+'</li>';
                }
                suggestion_dom.innerHTML = tag;
            },
            error:function(){
                console.log('fail');
            }
        });
    }

