//URL 관련 전역변수
const FsPoUrl = 'http://192.1.4.246:';
const FsPoPort = '14000';
const FsPoApp = 'FS';
const FsPo = FsPoUrl + FsPoPort + '/' + FsPoApp + '/';

//delete dialog 관련 전역변수
let postDeleteFunction;
let global;
let deleteTable;
let delete_service_url;
let deleteData;

//사원코드도움 관련 전역변수
let employeeCodeWidget;
let employeeNameWidget;
let departmentCodeWidget;
let departmentNameWidget;

//전표계정과목코드도움 관련 전역변수
let docAccountCodeHelpCodeWidget;
let docAccountCodeHelpNameWidget;
//const fStop3062Logic = Top.Controller.get("FStop3062Logic");

/* 소수점 사용자 설정 - 수량, 금액 별도로 자리수 관리
 * 환경설정 - 소수점 관리 UI가 생기고 사용자가 값을 입력할 수 있게 되면
 * 사용자 입력값을 받아오기 위해 아래와 같이 변경 예정
 * digit = n, quantity_digit = m, decimal_setting = [0, 1, 2]
*/

let digit = 3 ;
let quantity_digit = 4 ;
let decimal_setting= 0;


let ledgerDialogStartDate;
let ledgerDialogEndDate;
let ledgerDialogStartAccountCode;
let ledgerDialogEndAccountCode;
