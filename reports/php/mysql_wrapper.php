<?php
  header('Content-Type: application/json');

  $rows = array();

  if(!isset($_POST['request']) )
  {
    $rows['error'] = 'No query';
  }
  else
  {
    static $connection;
    if(!isset($connection))
    {
      $config = parse_ini_file('config.ini');
      $connection = mysqli_connect($config['hostname'],$config['username'],
          $config['password'],$config['dbname']);
    }

    if($connection === false)
    {
      return mysqli_connect_error();
    }

    $result = mysqli_query($connection, "SET sql_mode = '';");
    $result = mysqli_query($connection, $_POST['request']);

    if($result === false)
    {
      $rows['error'] = $result;
    }
    else
    {
      while ($row = mysqli_fetch_assoc($result))
      {
        $rows[] = $row;
      }
    }
  }

  echo json_encode($rows);
?>