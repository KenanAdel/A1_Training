create table if not exists customer_int (
    CustomerID int,
    Name string,
    Email string,
    Phone_Number string,
    Address string,
    JOIN_Date string,
    Start_Date string,
    End_Date string,
    Is_Current string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ("separatorChar" = ",", "quoteChar" = "\"", "escapeChar" = "\\")
STORED AS TEXTFILE;

LOAD DATA LOCAL INPATH '/home/itversity/customer_scd2_mixed.csv' INTO TABLE customer_int;

select * from customer_int;

--//////////////////////////////////////////////////////////////////////////




create external table if not exists customer_ext (
    CustomerID int,
    Name string,
    Email string,
    Phone_Number string,
    Address string,
    JOIN_Date string,
    Start_Date string,
    End_Date string,
    Is_Current string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ("separatorChar" = ",", "quoteChar" = "\"", "escapeChar" = "\\")
LOCATION '/user/itversity/customer_external_data';

LOAD DATA LOCAL INPATH '/home/itversity/customer_scd2_mixed.csv' INTO TABLE customer_ext;

select * from customer_ext;

DROP TABLE customer_int;
DROP TABLE customer_ext;

--//////////////////////////////////////////////////////////////////////////

create table if not exists customer_dim (
    CustomerID int,
    Name string,
    Email string,
    Phone_Number string,
    Address string,
    JOIN_Date string,
    Start_Date string,
    End_Date string,
    Is_Current string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ("separatorChar" = ",", "quoteChar" = "\"", "escapeChar" = "\\")
STORED AS TEXTFILE;

LOAD DATA LOCAL INPATH '/home/itversity/customer_scd2_mixed.csv' INTO TABLE customer_dim;


select CustomerID, Name, Address, Start_Date, End_Date, Is_Current 
from customer_dim 
order by CustomerID, Start_Date;



DROP table customer_dim;

--///////////////////////////////////////////////////////////////




create table if not exists customer_stage (
    CustomerID int,
    Name string,
    Email string,
    Phone_Number string,
    Address string,
    JOIN_Date string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ("separatorChar" = ",", "quoteChar" = "\"", "escapeChar" = "\\");

LOAD DATA LOCAL INPATH '/home/itversity/customer_updated.csv' INTO TABLE customer_stage;

select * from customer_stage;

DROP table customer_stage;

--///////////////////////////////////////////////////////////////



insert overwrite table customer_dim

select
    customerid, name, email, phone_number, address, join_date, start_date, end_date, is_current
from customer_dim
where is_current = '0'

union all

select
    d.customerid, d.name, d.email, d.phone_number, d.address, d.join_date, d.start_date, d.end_date, d.is_current
from customer_dim d
left join customer_stage s ON d.customerid = s.customerid
where d.is_current = '1'
  AND (
      s.customerid is null 
      OR (
          d.name = s.name 
          AND d.email = s.email 
          AND d.phone_number = s.phone_number 
          AND d.address = s.address
      )
  )

union all

select
    d.customerid, d.name, d.email, d.phone_number, d.address, d.join_date, d.start_date,
    date_format(current_date(), 'yyyy-MM-dd') as end_date,
    '0' as is_current
from customer_dim d
join customer_stage s ON d.customerid = s.customerid
where d.is_current = '1'
  AND (
      d.name != s.name 
      OR d.email != s.email 
      OR d.phone_number != s.phone_number 
      OR d.address != s.address 
  )

union all


select
    s.customerid, s.name, s.email, s.phone_number, s.address, s.join_date,
    date_format(current_date(), 'yyyy-MM-dd') as start_date,
    null as end_date,
    '1' as is_current
from customer_stage s
left join customer_dim d ON s.customerid = d.customerid AND d.is_current = '1'
where d.customerid is null
   OR (
      d.name != s.name 
      OR d.email != s.email 
      OR d.phone_number != s.phone_number 
      OR d.address != s.address
   );































