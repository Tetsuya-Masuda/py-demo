$(document).ready(function () {
    // on page load this will fetch data from our flask-app asynchronously
   $.ajax({url: '/word_cloud_def',data:{searchword:"会議"}, success: function (data) {
       // returned data is in string format we have to convert it back into json format
       var words_data = $.parseJSON(data);
       // we will build a word cloud into our div with id=word_cloud
       // we have to specify width and height of the word
       $('#title_wordcloud').jQCloud(words_data, {
           width: 200,
           height: 200
       });
   }});

   $.ajax({url: '/word_cloud_def',data:{searchword:"技術"}, success: function (data) {
       // returned data is in string format we have to convert it back into json format
       var words_data = $.parseJSON(data);
       // we will build a word cloud into our div with id=word_cloud
       // we have to specify width and height of the word
       $('#search_wordcloud').jQCloud(words_data, {
           width: 750,
           height: 300
       });

   }});


   $('#legendModalButton').click( function () {
		$('#legendModal').modal();
	});

   $('#search').click(function(e){
       if($('#searchword').val() == ''){
           return;
       }
       e.preventDefault();
       $.ajax({
           type:"GET",
           url:"/word_cloud_manual",
           data:{
               searchword : $('#searchword').val()
           },
           success:function(data){
               var word_json = $.parseJSON(data);
               if($('li').length == 1){
                   $('#search_wordcloud').jQCloud('destroy'); 
                   $('#search_wordcloud').jQCloud(word_json, {
                        classPattern:null,
                        fontSize:{
                            from:0.1,
                            to:0.02
                        },
                        width: 750,
                        height: 300,
                        autoResize:true
                    });
               }else{
                    $('#search_wordcloud').jQCloud('update',word_json); 
               }
               $('#searchword').val('');

               var words = [];
               var count = [];

                for(var i in word_json){
                    words.push(word_json[i].text);
                    count.push(word_json[i].weight);
                }

                var bind_data = {
                    labels:words,
                    datasets:[
                        {
                                label: 'word count',
                                backgroundColor: 'rgba(200, 200, 200, 0.75)',
                                borderColor: 'rgba(200, 200, 200, 0.75)',
                                hoverBackgroundColor: 'rgba(200, 200, 200, 1)',
                                hoverBorderColor: 'rgba(200, 200, 200, 1)',
                                data: count
                        }
                    ]

                };

                var ctx = $("#mychart");
                var barGraph = new Chart(ctx,{
                    type:'bar'
                });

                if(barGraph){
                    barGraph.destroy();
                }

                barGraph = new Chart(ctx,{
                    type:'bar',
                    data:bind_data,
                    options: {
                        scales: {
                            yAxes: [{
                                ticks: {
                                    beginAtZero:true
                                }
                            }]
                        }
                    }
                });

            },
           error:function(data){
                alert('NG');
           },
       });

       $('#searchwordlist').append('<li>' + $('#searchword').val() + '</li>');
   });

   $('#clear').click(function(e){
       e.preventDefault();
       $.ajax({
           type:"GET",
           url:"/word_cloud_clear",
           success:function(data){
                $('#search_wordcloud').jQCloud('destroy');
                $('li').remove();

                var ctx = $("#mychart");
                var barGraph = new Chart(ctx,{
                    type:'bar'
                });

                barGraph.destroy();

           }
       });
   });

   $('#word_cloud_word').on('click',function(){
        alert("aiueo");
   });

});
