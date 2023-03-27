pragma solidity 0.8.17;

import "./TradeHandlerHelper.sol";

contract Treasury {
    address payable public governance;
    address payable public pendingGovernance;

    event SweptToken(address token, uint amount);
    event SweptETH(uint amount);
    event PendingGovernance(address newPendingGov);
    event AcceptedGovernance(address newGov);

    constructor(address payable _governance) public {
        governance = _governance;
    }

    modifier onlyGovernance() {
        require(msg.sender == governance, "!governance");
        _;
    }

    function setGovernance(address payable _newGov) external onlyGovernance {
        require(_newGov != address(0));
        pendingGovernance = _newGov;
        emit PendingGovernance(_newGov);
    }

    function acceptGovernance() external {
        require(msg.sender == pendingGovernance, "!pendingGovernance");
        governance = pendingGovernance;
        delete pendingGovernance;
        emit AcceptedGovernance(governance);
    }

    function sweep(
        address[] calldata _tokens,
        uint256[] calldata _amounts
    ) external onlyGovernance {
        uint256 _size = _tokens.length;
        require(_size == _amounts.length);

        for (uint256 i = 0; i < _size; i++) {
            if (_tokens[i] == address(0)) {
                // Native ETH
                TradeHandlerHelper.safeTransferETH(governance, _amounts[i]);
                emit SweptETH(_amounts[i]);
            } else {
                // ERC20s
                TradeHandlerHelper.safeTransfer(
                    _tokens[i],
                    governance,
                    _amounts[i]
                );
                emit SweptToken(_tokens[i], _amounts[i]);
            }
        }
    }

    // `fallback` is called when msg.data is not empty
    fallback() external payable {}

    // `receive` is called when msg.data is empty
    receive() external payable {}
}
