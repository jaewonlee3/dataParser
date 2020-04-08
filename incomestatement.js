

Top.Controller.create('FI_1Q_TOPLogic', {
	changeIsTab : function(event, widget) {
	//선택된 탭으로 전환시켜주는 함수
		a = widget;
}, selectIsYear : function(event, widget) {
	//입력된 연도와 월에 따른 손익계산서들을 보여주는 함수
	//3단계로 구성되고 순차적으로 실행됨 
	//1. 해당되는 연, 월의 데이터들을 전표테이블에서 가져와서 손익계산서 계정과목에 맞게 계산하여 손익계산서 테이블에 입력
	//2. 입력된 손익계산서 테이블을 읽어와서 테이블뷰에 반영(과목별, 제출용 손익계산서)
	//3. 입력된 손익계산서 테이블의 계정과목들과 그 외에 모든 계정과목들을 함께 읽어와서 하나의 테이블뷰에 반영(표준(법인)용 손익계산서)
	
	
	
	Top.Ajax.execute({
		
		//url : `${FsPo}IC/InsertDate01?action=SO`, //1번 단계에 해당. 입력받은 연도의 1월 1일부터 입력받은 월의 말일까지의 데이터를 가져와서 가공
		url: 'http://192.1.4.246:14000/FS/IC/InsertDate01?action=SO',
		type : 'POST',
		dataType : 'json',
		contentType: 'application/json; charset=UTF-8',
		data : JSON.stringify({
			"dto":{
				"MONTH_IN" : Top.Dom.selectById('SelectBox254').getSelectedText(), //입력받는 월
				"YEAR_IN" : Top.Dom.selectById("TextField206").getText() //입력받는 연도
			}
		}),
		success:function(result){ 
			
			Top.Ajax.execute({
				
				//url : `${FsPo}IC/ReadAccountIS?action=SO`, //2번 단계에 해당. 손익계산서 테이블을 읽어와서 테이블 뷰에 반영
				url: 'http://192.1.4.246:14000/FS/IC/ReadAccountIS?action=SO',
				type : 'POST',
				dataType : 'json',
				contentType: 'application/json; charset=UTF-8',
				data : JSON.stringify({
					"dto":{
						"MONTH_IN" : Top.Dom.selectById('SelectBox254').getSelectedText() //전기분 손익계산서에서 입력받은 월까지의 데이터를 가져오기 위해, 입력받은 월 사용						
					}
				}),
				success:function(result){ 
					//1번과 2번 단계가 잘 작동되면 이 때 가져온 손익계산서 데이터들을 테이블뷰에 반영시켜줌
					dto_AccountIS = result["dto"]
					drIncomeStatementAccountISFull.diIncomeStatementAccountISFull = dto_AccountIS.ISListDO
					tvISAccount = Top.Dom.selectById("ISAccountTable")
					
					
					drIncomeStatementAccount.diIncomeStatementAccount = dto_AccountIS.ISListDO					
					tvISAccount2 = Top.Dom.selectById("ISAccountTable_1")					
					tvISAccount2.update(); 
					
					
					tvISAccount.update(); 
					
					
					
					Top.Ajax.execute({
						
						//url : `${FsPo}IC/ReadIS?action=SO`, //3번 단계에 해당. 표준(법인)용 손익계산서 데이터를 읽어온다.
						url: 'http://192.1.4.246:14000/FS/IC/ReadIS?action=SO',
						type : 'POST',
						dataType : 'json',
						contentType: 'application/json; charset=UTF-8',
						data : JSON.stringify({
							"dto":{
								"MONTH_IN" : Top.Dom.selectById('SelectBox254').getSelectedText() //입력받는 월
							}
						}),
						success:function(result){ 
							//3번 단계가 잘 작동되면 이 데이터들을 테이블뷰에 반영시켜줌
							dto_IS = result["dto"];															
							drIncomeStatement.diIncomeStatement = dto_IS.ISListDO
								
							tvIS= Top.Dom.selectById("TableView32");
							tvIS.update();			
							
						},
						error : function(error){
							alert("표준(법인)용 손익계산서를 불러오는 중 오류가 발생하였습니다.");
						}
					});//end of 3rd ajax(표준(법인)용 손익계산서)
					
					
					
					
					
				},
				error:function(result){
					alert("손익계산서(과목별)를 불러오는 중 오류가 발생하였습니다.");
				}
			})	//end of 2nd ajax(과목별, 제출용 손익계산서 부터)	
					
			
			
		},
		error:function(result){
			alert("손익계산서에 입력될 전표 데이터를 불러오는 중 오류가 발생하였습니다.");
		}
	})//end of 1st ajax(손익계산서용 데이터 불러오고 가공하는 과정)	
	
	
	
	}, goExpenseMainTemp : function(event, widget) {
		Top.Dom.selectById("IncomeStatementMainLayout").src("ExpenseClaimMainLayout.html");
}
//end of selectIsYear function
	
})





