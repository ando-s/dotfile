# 共有の settings.json（$shared）に、マシン固有の settings.machine.json（$machine）を重ねる。
# オブジェクトはキーごとに重ね、値が食い違えばマシン固有の値を使う。
# 配列（permissions.allow・hooks の各イベントなど）は、共有の後ろにマシン固有の要素を足す。同じ要素は1つにする。
def merge($a; $b):
  if ($a | type) == "object" and ($b | type) == "object" then
    reduce (($a | keys) + ($b | keys) | unique)[] as $k ({};
      .[$k] =
        if ($a | has($k)) and ($b | has($k)) then merge($a[$k]; $b[$k])
        elif ($b | has($k)) then $b[$k]
        else $a[$k]
        end)
  elif ($a | type) == "array" and ($b | type) == "array" then
    $a + ($b - $a)
  else
    $b
  end;

merge($shared[0]; $machine[0])
