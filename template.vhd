library IEEE;
use IEEE.STD_LOGIC_1164.all;
use IEEE.NUMERIC_STD.all;

-- pMem interface
entity pMem is
  port(
    pAddr : in unsigned(14 downto 0);
    pData : out unsigned(15 downto 0));
end pMem;

architecture Behavioral of pMem is

-- program Memory
type p_mem_t is array (0 to <MAX_INDEX>) of unsigned(7 downto 0);
constant p_mem_c : p_mem_t := <BUFFER>

  signal p_mem : p_mem_t := p_mem_c;


begin  -- pMem
  pData <= p_mem(to_integer(pAddr(<MAX_BIT> downto 0) + 1)) & p_mem(to_integer(pAddr(<MAX_BIT> downto 0)));

end Behavioral;
